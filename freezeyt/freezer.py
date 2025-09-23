import sys
from pathlib import Path, PurePosixPath
import io
import itertools
import functools
import dataclasses
from typing import Callable, Optional, Mapping, Set, Generator, Dict, Union
from typing import Tuple, List, TypeVar, Any, cast
import asyncio
import inspect
import re
import os

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header, parse_list_header

import freezeyt
import freezeyt.actions
from freezeyt.encoding import encode_wsgi_path, decode_input_path
from freezeyt.encoding import encode_file_path
from freezeyt.filesaver import FileSaver
from freezeyt.dictsaver import DictSaver
from freezeyt.util import import_variable_from_module
from freezeyt.util import InfiniteRedirection, ExternalURLError
from freezeyt.util import UnexpectedStatus, MultiError, TaskStatus
from freezeyt.urls import AppURL, PrefixURL
from freezeyt.compat import warnings_warn
from freezeyt.compat import StartResponse, WSGIEnvironment, WSGIApplication
from freezeyt import hooks
from freezeyt.saver import Saver
from freezeyt.middleware import Middleware
from freezeyt.actions import ActionFunction
from freezeyt.url_finders import UrlFinder
from freezeyt.extra_files import get_extra_files, get_url_parts_from_directory
from freezeyt.types import Config, SaverResult, WSGIHeaderList
from freezeyt.types import WSGIExceptionInfo


MAX_RUNNING_TASKS = 100

# HTTP status description for status_handlers:
# 3 digits, or 1 digit and 'xx'.
STATUS_KEY_RE = re.compile('^[0-9]([0-9]{2}|xx)$')


def freeze(app: Optional[WSGIApplication], config: Config) -> SaverResult:
    return asyncio.run(freeze_async(app, config))


async def freeze_async(
    app: Optional[WSGIApplication],
    config: Config,
) -> SaverResult:
    freezer = Freezer(app, config)
    try:
        await freezer.prepare()
        freezer.call_hook('start', freezer.freeze_info)
        await freezer.handle_urls()
        await freezer.handle_redirects()
        return await freezer.finish()
    except:
        await freezer.cancel_tasks()
        raise


DEFAULT_URL_FINDERS = {
            'text/html': 'get_html_links_async',
            'text/css': 'get_css_links_async'
        }


K = TypeVar('K')
Func = TypeVar('Func', bound=Callable)

def parse_handlers(
    handlers: Mapping[K, Union[str, Func]],
    default_module: Optional[str]=None,
    label: str="Handler",
) -> Dict[K, Func]:
    """Map handler/action as callable
    """
    result = {}

    for key, handler_or_name in handlers.items():
        if isinstance(handler_or_name, str):
            handler = import_variable_from_module(
                handler_or_name,
                default_module_name=default_module
            )
        else:
            handler = handler_or_name

        if not callable(handler):
            raise TypeError(
                f"{label} for {key!r} in configuration must be "
                + f"a string or a callable, not a {type(handler)}!"
            )

        result[key] = handler

    return result


def default_url_to_path(path: str) -> str:
    if path.endswith('/') or not path:
        path = path + 'index.html'
    return encode_file_path(path)


def get_path_from_url(
    url: AppURL, url_to_path: Callable[[str], str],
) -> PurePosixPath:
    """Return the disk path to which `url` should be saved.

    `url_to_path` is the function given in the config. It takes a string
    and returns a string.
    """
    result = PurePosixPath(url_to_path(url.relative_path))

    if result.is_absolute():
        raise ValueError(
            f"Path may not be absolute: {result}(from {url})"
        )
    assert '.' not in result.parts
    if '..' in result.parts:
        raise ValueError(
            f"Path may not contain /../ segment: {result}(from {url})"
        )

    return result

@dataclasses.dataclass
class Response:
    headers: Headers
    status: str


@dataclasses.dataclass
class Task:
    path: PurePosixPath
    urls: "Set[AppURL]"
    freezer: "Freezer"
    response: Optional[Response] = None
    redirects_to: "Optional[Task]" = None
    reasons: set = dataclasses.field(default_factory=set)
    asyncio_task: "Optional[FreezeytAsyncioTask]" = None
    urls_redirecting_to_self: set = dataclasses.field(default_factory=set)
    exception: Optional[Exception] = None

    def __repr__(self) -> str:
        return f"<Task for {self.path}, {self.status.name}>"

    def add_url(self, url: AppURL) -> None:
        self.urls.add(url)

    def get_a_url(self) -> AppURL:
        """Get an arbitrary one of the task's URLs."""
        # we need to ensure that get_a_url() will get the right one
        # when there are urls redirection to itself
        return next(iter(self.urls - self.urls_redirecting_to_self))

    @property
    def status(self) -> TaskStatus:
        for status, collection in self.freezer.task_collections.items():
            if self.path in collection:
                return status
        raise ValueError(f'Task not registered with freezer: {self}')

    def update_status(self, old_status, new_status):
        assert self.status == old_status
        old_collection = self.freezer.task_collections[old_status]
        del old_collection[self.path]
        new_collection = self.freezer.task_collections[new_status]
        assert self.path not in new_collection
        new_collection[self.path] = self

    def fail(self, exception):
        if self.freezer.fail_fast:
            raise exception
        if self.exception is not None:
            # The task already failed; we shouldn't do any more operations
            # on it. If we do and they fail, raise that error directly.
            raise exception
        self.exception = exception
        self.update_status(self.status, TaskStatus.FAILED)
        self.freezer.call_hook('page_failed', hooks.TaskInfo(self))

class FreezeytAsyncioTask(asyncio.Task):
    """
    asyncio.Task with an extra attribute to store the underlying freezeyt Task.

    For typing only.
    """
    freezeyt_task: Task

class IsARedirect(BaseException):
    """Raised when a page redirects and freezing it should be postponed"""

class RedirectToSamePath(BaseException):
    """Raised when a page redirects to url with same freezing path on disk as the page"""

class IgnorePage(BaseException):
    """Raised when freezing a page should be ignored"""

class VersionMismatch(ValueError):
    """Raised when major version in config is not correct"""

def needs_semaphore(func):
    """Decorator for a "task" method that holds self.semaphore when running"""
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.semaphore:
            result = await func(self, *args, **kwargs)
        return result
    return wrapper


TaskCollection = Dict[PurePosixPath, Task]
ExtraPagesConfig = Union[
    Dict[str, Union[Generator, str]],
    str,
    Generator,
    Tuple[()],
]

class Freezer:
    saver: Saver
    task_collections: Dict[TaskStatus, TaskCollection]
    done_tasks: TaskCollection
    redirecting_tasks: TaskCollection
    inprogress_tasks: TaskCollection
    failed_tasks: TaskCollection
    extra_pages: ExtraPagesConfig
    hooks: Dict[str, List[Callable]]
    url_to_path: Callable[[str], str]
    fail_fast: bool

    url_finders: Dict[str, UrlFinder]
    status_handlers: Dict[str, ActionFunction]

    def __init__(self, app: Optional[WSGIApplication], config: Config):
        self.config = dict(config)
        del config  # we always want to use `self.config` from now on

        self.check_version(self.config.get('version'))

        self.freeze_info = hooks.FreezeInfo(self)

        app_config = self.config.get('app')
        if app is None:
            if app_config is None:
                raise ValueError("Application is required")

            if isinstance(app_config, str):
                # config file/variable or command line argument
                app = import_variable_from_module(
                    app_config, default_variable_name='app',
                )
            else:
                # config variable - app as object
                app = app_config
        else:
            if app_config is not None:
                raise ValueError("Application is specified both as parameter and in configuration")
            app = app

        # The original app, to be passed back to the user when needed
        self.user_app = app

        # The app we call, wrapped in Middleware
        self.app = Middleware(app, self.config)

        self.fail_fast = self.config.get('fail_fast', False)

        if self.config.get("gh_pages", False):
            plugins = self.config.setdefault('plugins', [])
            if 'freezeyt.plugins:GHPagesPlugin' not in plugins:
                plugins.append('freezeyt.plugins:GHPagesPlugin')
        if self.config.get("gh_pages", False) is False:
            plugins = self.config.setdefault('plugins', [])
            if 'freezeyt.plugins:GHPagesPlugin' in plugins:
                plugins.remove('freezeyt.plugins:GHPagesPlugin')

        CONFIG_DATA = (
            ('extra_pages', ()),
            ('url_to_path', default_url_to_path)
        )
        for attr_name, default in CONFIG_DATA:
            setattr(self, attr_name, self.config.get(attr_name, default))

        if isinstance(self.url_to_path, str):
            self.url_to_path = import_variable_from_module(self.url_to_path)

        if self.config.get('use_default_url_finders', True):
            _url_finders = dict(
                DEFAULT_URL_FINDERS, **self.config.get('url_finders', {})
            )
        else:
            _url_finders = self.config.get('url_finders', {})

        self.url_finders = parse_handlers(
            _url_finders, default_module='freezeyt.url_finders', label="URL finder"
        )

        _status_handlers = self.config.get('status_handlers', {})
        for key in _status_handlers:
            if not STATUS_KEY_RE.fullmatch(key):
                raise ValueError(
                    "Status description must be string with three digits (e.g. 200)"
                    + " or a status group, one digit with 'xx' (e.g. 2xx),"
                    + f" got f{key!r}"
                )

        self.status_handlers = parse_handlers(
            _status_handlers, default_module='freezeyt.actions', label="Status handler"
        )

        prefix = self.config.get('prefix', 'http://localhost:8000/')

        # Decode path in the prefix URL.
        # Save the parsed version of prefix as self.prefix
        prefix_parsed = PrefixURL(prefix)
        decoded_path = decode_input_path(prefix_parsed.path)
        if not decoded_path.endswith('/'):
            raise ValueError('prefix must end with /')
        self.prefix = prefix_parsed._replace_path(path=decoded_path)

        output = self.config['output']
        if isinstance(output, str):
            output = {'type': 'dir', 'dir': output}

        if output['type'] == 'dict':
            self.saver = DictSaver()
        elif output['type'] == 'dir':
            try:
                output_dir = output['dir']
            except KeyError:
                raise ValueError("output directory not specified")
            self.saver = FileSaver(Path(output_dir), self.prefix)
        else:
            raise ValueError(f"unknown output type {output['type']}")

        self.warnings: List[str] = []
        # The tasks for individual pages are tracked in the followng sets
        # (actually dictionaries: {task.path: task})
        # Each task must be in exactly in one of these.
        self.done_tasks = {}
        self.redirecting_tasks = {}
        self.inprogress_tasks = {}
        self.failed_tasks = {}
        self.task_collections = {
            TaskStatus.DONE: self.done_tasks,
            TaskStatus.REDIRECTING: self.redirecting_tasks,
            TaskStatus.IN_PROGRESS: self.inprogress_tasks,
            TaskStatus.FAILED: self.failed_tasks,
        }
        if "//" in prefix_parsed.path:
            self.warnings.append(
                f"Freezeyt reduces multiple consecutive slashes in {prefix!r} to one"
            )

        self.hooks = {}
        for name, funcs in self.config.get('hooks', {}).items():
            for func in funcs:
                if isinstance(func, str):
                    func = import_variable_from_module(func)
                self.add_hook(name, func)

        for plugin in self.config.get('plugins', {}):
            if isinstance(plugin, str):
                plugin = import_variable_from_module(plugin)
            plugin(self.freeze_info)

        self.semaphore = asyncio.Semaphore(MAX_RUNNING_TASKS)


    def check_version(self, config_version: Union[str, float, None]) -> None:
        if config_version is None:
            return
        if not isinstance(config_version, float):
            main_version = str(config_version).split(".")[0]
        else:
            raise VersionMismatch("The specified version has to be string or int i.e. 1, 1.1 or '1', '1.1'.")

        current_version = freezeyt.__version__.split(".")[0]
        if main_version != current_version:
            raise VersionMismatch("The specified version does not match the freezeyt main version.")

    def add_hook(self, hook_name: str, func: Callable) -> None:
        self.hooks.setdefault(hook_name, []).append(func)

    async def cancel_tasks(self) -> None:
        cancelled_atasks = []
        while self.inprogress_tasks:
            path, task = self.inprogress_tasks.popitem()
            assert task.asyncio_task is not None
            task.asyncio_task.cancel()
            cancelled_atasks.append(task.asyncio_task)
        for atask in cancelled_atasks:
            try:
                await atask
            except asyncio.CancelledError:
                pass

    async def finish(self) -> SaverResult:
        success = not self.failed_tasks
        cleanup = self.config.get("cleanup", True)
        result = await self.saver.finish(success, cleanup)
        if success:
            self.call_hook('success', self.freeze_info)

            for task in self.done_tasks.values():
                if len(task.urls) > 1:
                    display_urls = sorted(
                        [url.relative_path_with_query for url in task.urls]
                    )

                    self.warnings.append(
                        f"Static file '{task.path}' is requested from"
                        f" different URLs {display_urls}"
                    )

            for warning in self.warnings:
                print(f"[WARNING] {warning}")
            return result
        raise MultiError(self.failed_tasks.values())

    def add_task(
        self,
        url: AppURL,
        *,
        reason: Optional[str] = None,
    ) -> Optional[Task]:
        """Add a task to freeze the given URL

        If no task is added (e.g. for external URLs), return None.
        """
        task = self._add_task(url, reason=reason)
        if task and task.asyncio_task is None:
            coroutine = self.handle_one_task(task)
            task.asyncio_task = cast(
                FreezeytAsyncioTask,
                asyncio.create_task(
                    coroutine,
                    name=str(task.path),
                ),
            )
            task.asyncio_task.freezeyt_task = task
        return task

    def _add_task(
        self,
        url: AppURL,
        *,
        reason: Optional[str] = None,
    ) -> Optional[Task]:
        path = get_path_from_url(url, self.url_to_path)

        for collection in self.task_collections.values():
            if path in collection:
                task = collection[path]
                task.add_url(url)
                break
        else:
            # The `else` branch is entered if the loop ended normally
            # (not with `break`, or exception, return, etc.)
            # Here, this means the task wasn't found.
            task = Task(path, {url}, self)
            self.inprogress_tasks[path] = task
        if reason:
            task.reasons.add(reason)
        return task

    async def prepare(self) -> None:
        """Preparatory method for creating tasks and preparing the saver."""
        # prepare the tasks
        self.add_task(self.prefix.as_app_url(), reason='site root (homepage)')
        for url_part, kind, content_or_path in get_extra_files(self.config):
            if kind == 'content':
                # join part with path, otherwise filename 'http:' overwrite prefix
                assert self.prefix.path.endswith('/')
                assert not url_part.startswith('/')
                url_part = self.prefix.path + url_part
                self.add_task(
                    self.prefix.join(url_part),
                    reason="from extra_files",
                )
            elif kind == 'path':
                assert isinstance(content_or_path, Path)
                for part in get_url_parts_from_directory(
                    url_part, content_or_path
                ):
                # join part with path, otherwise filename 'http:' overwrite prefix
                    assert self.prefix.path.endswith('/')
                    assert not url_part.startswith('/')
                    part = self.prefix.path + part
                    self.add_task(
                        self.prefix.join(part),
                        reason="from extra_files",
                    )
            else:
                raise ValueError(kind)
        self._add_extra_pages(self.extra_pages)

        # and at the end prepare the saver
        return await self.saver.prepare()

    def start_response(
        self,
        task: Task,
        url: AppURL,
        wsgi_write: Func,
        status: str,
        headers: WSGIHeaderList,
        exc_info: WSGIExceptionInfo = None,
    ) -> Func:
        """WSGI start_response hook

        The application we are freezing will call this method
        and supply the status, headers, exc_info arguments.
        (self and wsgi_write are provided by freezeyt.)

        See: https://www.python.org/dev/peps/pep-3333/#the-start-response-callable

        Arguments:
            wsgi_write: function that the application can call to output data
            status: HTTP status line, like '200 OK'
            headers: HTTP headers (list of tuples)
            exc_info: Information about a server error, if any.
                Will be raised if given.
        """
        if exc_info:
            exc_type, value, traceback = exc_info
            if value is not None:
                raise value

        if task.response is not None:
            raise AssertionError('WSGI app called start_response twice')
        task.response = Response(
            headers=Headers(headers),
            status=status,
        )

        status_handler_name: Optional[str]
        status_handler_name = task.response.headers.get('Freezeyt-Action')

        # handle redirecting to same filepath like source URL
        if status.startswith('3'):
            location = task.response.headers.get('Location')
        else:
            location = None
        if location is not None:
            try:
                redirect_url = url.join(location)
            except ExternalURLError:
                pass
            else:
                redirect_path = get_path_from_url(
                    redirect_url, self.url_to_path,
                )
                # compare if source path and final path of redirect are same
                # If they are, apply special logic: consider the target of
                # the redirection as the page we're supposed to save.
                same_path = redirect_path == task.path
                # compare if source url and final url of redirect are different.
                # If they are not it means a infinite redirect and
                # it should be handle as other tasks
                not_same_urls = redirect_url.path != url.path

                if same_path and not_same_urls:
                    # Only do this if we haven't seen this URL yet.
                    # If we are, skip this special case. (We're in a redirect
                    # loop and will probably fail later.)
                    if redirect_url not in task.urls_redirecting_to_self:
                        task.add_url(redirect_url)
                        task.urls_redirecting_to_self.add(url)
                        task.response = None  # Ignore this response
                        raise RedirectToSamePath()

        status_handler: Optional[ActionFunction] = None
        if status_handler_name:
            status_handler = freezeyt.actions._ACTIONS[status_handler_name]

        if not status_handler:
            # Get a handler for the particular status from configuration
            status_handler = self.status_handlers.get(status[:3])

        if not status_handler:
            # If a handler for the particular status isn't found,
            # get handler for a group of statuses
            status_handler = self.status_handlers.get(status[0] + 'xx')

        if not status_handler:
            # Still not found? Use the default handler
            if status.startswith('200'):
                # default behaviour for status 200
                status_handler = freezeyt.actions.save
            else:
                # default behaviour for everything but 200
                raise UnexpectedStatus(url, status, location)

        status_action = status_handler(hooks.TaskInfo(task))

        if status_action == 'save':
            return wsgi_write
        elif status_action == 'ignore':
            raise IgnorePage()
        elif status_action == 'follow':
            raise IsARedirect()
        else:
            raise UnexpectedStatus(url, status, location)


    def _add_extra_pages(
        self,
        extras: ExtraPagesConfig,
    ) -> None:
        """Add URLs of extra pages from config.

        Handles both literal URLs and generators.
        """
        for extra in extras:
            if isinstance(extra, dict):
                try:
                    generator = extra['generator']
                except KeyError:
                    raise ValueError(
                        'extra_pages must be strings or dicts with '
                        + f'a "generator" key, not `{extra}`'
                    )
                if isinstance(generator, str):
                    generator = import_variable_from_module(generator)
                self._add_extra_pages(generator(self.user_app))
            elif isinstance(extra, str):
                if extra.startswith('/'):
                    warnings_warn(
                        f'extra page URL must not start with slash: {extra!r}',
                        DeprecationWarning,
                        skip_file_prefixes=(
                            os.path.dirname(__file__),
                            os.path.dirname(asyncio.__file__),
                        ),
                    )
                url = self.prefix.join(decode_input_path(extra))
                try:
                    self.add_task(
                        url,
                        reason='extra page',
                    )
                except ExternalURLError:
                    raise ExternalURLError(
                        f'External URL specified in extra_pages: {url}'
                    )
            else:
                generator = extra
                self._add_extra_pages(generator(self.user_app))

    async def handle_urls(self) -> None:
        while self.inprogress_tasks:
            done, pending = await asyncio.wait(
                {t.asyncio_task for t in self.inprogress_tasks.values()
                 if t.asyncio_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for done_asyncio_task in done:
                task = done_asyncio_task.freezeyt_task
                assert task.asyncio_task is done_asyncio_task

                try:
                    await task.asyncio_task
                except Exception as exc:
                    task.fail(exc)
                if task.path in self.inprogress_tasks:
                    raise ValueError(
                        f'{task} is in_progress after it was handled')

    @needs_semaphore
    async def handle_one_task(self, task: Task) -> None:
        # Get an URL from the task's set of URLs
        url = task.get_a_url()

        # url_string should not be needed (except for debug messages)
        url_string = str(url)

        path_info = url.path

        if path_info.startswith(self.prefix.path):
            path_info = "/" + path_info[len(self.prefix.path):]

        environ: WSGIEnvironment = {
            'SERVER_NAME': self.prefix.hostname,
            'SERVER_PORT': str(self.prefix.port),
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': encode_wsgi_path(path_info),
            'SCRIPT_NAME': encode_wsgi_path(self.prefix.path),
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'SERVER_SOFTWARE': f'freezeyt/{freezeyt.__version__}',

            'wsgi.version': (1, 0),
            'wsgi.url_scheme': self.prefix.scheme,
            'wsgi.input': io.BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,

            'freezeyt.freezing': True,
        }

        # The WSGI application can output data in two ways:
        # - by a "write" function, which, in our case, will append
        #   any data to a list, `wsgi_write_data`
        # - (preferably) by returning an iterable object.

        # See: https://www.python.org/dev/peps/pep-3333/#the-write-callable

        # Set up the wsgi_write_data, and make its `append` method
        # available to `start_response` as first argument:
        wsgi_write_data: List[bytes] = []
        start_response: StartResponse = functools.partial(
            self.start_response,
            task,
            url,
            wsgi_write_data.append,
        )

        # Call the application. All calls to write (wsgi_write_data.append)
        # must be done as part of this call.
        try:
            result_iterable = self.app(environ, start_response)
        except IsARedirect:
            return
        except IgnorePage:
            task.update_status(TaskStatus.IN_PROGRESS, TaskStatus.DONE)
            return
        except RedirectToSamePath:
            return await self.handle_one_task(task)

        try:
            # Combine the list of data from write() with the returned
            # iterable object.
            full_result = itertools.chain(
                wsgi_write_data,
                result_iterable,
            )

            await self.saver.save_to_filename(task.path, full_result)

        finally:
            close = getattr(result_iterable, 'close', None)
            if close is not None:
                close()

        assert task.response is not None
        finder_name = task.response.headers.get('Freezeyt-URL-Finder')
        if finder_name is not None:
            url_finder = import_variable_from_module(
                finder_name,
                default_module_name='freezeyt.url_finders',
            )
        else:
            content_type = task.response.headers.get('Content-Type')
            mime_type, encoding = parse_options_header(content_type)
            url_finder = self.url_finders.get(mime_type)
        if url_finder is not None:
            with await self.saver.open_filename(task.path) as f:
                finder_result = url_finder(
                    f, url_string, task.response.headers.to_wsgi_list()
                )
                if inspect.iscoroutine(finder_result):
                    links = await finder_result
                else:
                    links = finder_result
                if inspect.isasyncgen(links):
                    new_links = []
                    async for link in links:
                        new_links.append(link)
                    links = new_links
                for link_text in links:
                    try:
                        new_url = url.join(link_text)
                    except ExternalURLError:
                        pass
                    else:
                        self.add_task(
                            new_url,
                            reason=f'linked from: {task.path}',
                        )

        if self.config.get('urls_from_link_headers', True):
            for link_header in task.response.headers.getlist('Link'):
                for link in parse_list_header(link_header):
                    link = link.strip()
                    if not link.startswith('<'):
                        raise ValueError(f'Invalid Link header: {link!r}')
                    link_text, sep, rest = link[1:].partition('>')
                    if not sep:
                        raise ValueError(f'Invalid Link header: {link!r}')
                    try:
                        new_url = url.join(link_text)
                    except ExternalURLError:
                        pass
                    else:
                        self.add_task(
                            new_url,
                            reason=f'Link header from: {task.path}',
                        )

        task.update_status(TaskStatus.IN_PROGRESS, TaskStatus.DONE)

        self.call_hook('page_frozen', hooks.TaskInfo(task))

    @needs_semaphore
    async def handle_redirects(self) -> None:
        """Save copies of target pages for redirect_policy='follow'"""
        while self.redirecting_tasks:
            saved_something = False
            for key, task in list(self.redirecting_tasks.items()):
                assert task.redirects_to is not None
                if task.redirects_to.status == TaskStatus.FAILED:
                    # Don't process redirects to a failed pages
                    task.update_status(TaskStatus.REDIRECTING, TaskStatus.DONE)
                    continue
                if task.redirects_to.status != TaskStatus.DONE:
                    continue

                with await self.saver.open_filename(task.redirects_to.path) as f:
                    await self.saver.save_to_filename(task.path, f)
                self.call_hook('page_frozen', hooks.TaskInfo(task))
                task.update_status(TaskStatus.REDIRECTING, TaskStatus.DONE)
                saved_something = True
            if not saved_something:
                # Get some task (the first one we get by iteration) for the
                # error message.
                failing_task = None
                for task in self.redirecting_tasks.values():
                    failing_task = task
                    break
                if failing_task:
                    failing_task.fail(InfiniteRedirection(task))

    def call_hook(self, hook_name: str, *arguments: Any) -> None:
        for hook in self.hooks.get(hook_name, ()):
            hook(*arguments)
