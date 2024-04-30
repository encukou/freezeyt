import sys
from pathlib import Path, PurePosixPath
import io
import itertools
import functools
import dataclasses
from typing import Callable, Optional, Mapping, Set, Generator, Dict, Union
from typing import Tuple, List, TypeVar, Any
import asyncio
import inspect
import re
import urllib.parse

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header, parse_list_header

import freezeyt
import freezeyt.actions
from freezeyt.encoding import encode_wsgi_path, decode_input_path
from freezeyt.encoding import encode_file_path
from freezeyt.filesaver import FileSaver
from freezeyt.dictsaver import DictSaver
from freezeyt.util import parse_absolute_url, is_external, urljoin
from freezeyt.util import import_variable_from_module
from freezeyt.util import InfiniteRedirection, ExternalURLError
from freezeyt.util import UnexpectedStatus, MultiError, AbsoluteURL, TaskStatus
from freezeyt.compat import asyncio_run, asyncio_create_task
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
    return asyncio_run(freeze_async(app, config))


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
    prefix: AbsoluteURL, url: AbsoluteURL, url_to_path: Callable[[str], str],
) -> PurePosixPath:
    """Return the disk path to which `url` should be saved.

    `url_to_path` is the function given in the config. It takes a string
    and returns a string.

    Both arguments should be results of parse_absolute_url.
    """
    if is_external(url, prefix):
        raise ValueError(f'external url {url}')

    path = url.path

    if path.startswith(prefix.path):
        path = path[len(prefix.path):]

    result = PurePosixPath(url_to_path(path))

    if result.is_absolute():
        url_text = urllib.parse.urlunsplit(url)
        raise ValueError(
            f"Path may not be absolute: {result}(from {url_text})"
        )
    assert '.' not in result.parts
    if '..' in result.parts:
        url_text = urllib.parse.urlunsplit(url)
        raise ValueError(
            f"Path may not contain /../ segment: {result}(from {url_text})"
        )

    return result

@dataclasses.dataclass
class Task:
    path: PurePosixPath
    urls: "Set[AbsoluteURL]"
    freezer: "Freezer"
    response_headers: Optional[Headers] = None
    response_status: Optional[str] = None
    redirects_to: "Optional[Task]" = None
    reasons: set = dataclasses.field(default_factory=set)
    asyncio_task: "Optional[asyncio.Task]" = None

    def __repr__(self) -> str:
        return f"<Task for {self.path}, {self.status.name}>"

    def get_a_url(self) -> AbsoluteURL:
        """Get an arbitrary one of the task's URLs."""
        return next(iter(self.urls))

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

class IsARedirect(BaseException):
    """Raised when a page redirects and freezing it should be postponed"""

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
        prefix_parsed = parse_absolute_url(prefix)
        decoded_path = decode_input_path(prefix_parsed.path)
        if not decoded_path.endswith('/'):
            raise ValueError('prefix must end with /')
        self.prefix = prefix_parsed._replace(path=decoded_path)

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
                    self.warnings.append(
                        f"Static file '{task.path}' is requested from"
                        f" different URLs {sorted([url.path for url in task.urls])}"
                    )

            for warning in self.warnings:
                print(f"[WARNING] {warning}")
            return result
        raise MultiError(self.failed_tasks.values())

    def add_task(
        self,
        url: AbsoluteURL,
        *,
        external_ok: bool = False,
        reason: Optional[str] = None,
    ) -> Optional[Task]:
        """Add a task to freeze the given URL

        If no task is added (e.g. for external URLs), return None.
        """
        task = self._add_task(url, external_ok=external_ok, reason=reason)
        if task and task.asyncio_task is None:
            coroutine = self.handle_one_task(task)
            task.asyncio_task = asyncio_create_task(
                coroutine,
                name=str(task.path),
            )
        return task

    def _add_task(
        self,
        url: AbsoluteURL,
        *,
        external_ok: bool = False,
        reason: Optional[str] = None,
    ) -> Optional[Task]:
        if is_external(url, self.prefix):
            if external_ok:
                return None
            raise ExternalURLError(f'Unexpected external URL: {url}')

        path = get_path_from_url(self.prefix, url, self.url_to_path)

        for collection in self.task_collections.values():
            if path in collection:
                task = collection[path]
                task.urls.add(url)
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
        self.add_task(self.prefix, reason='site root (homepage)')
        for url_part, kind, content_or_path in get_extra_files(self.config):
            if kind == 'content':
                # join part with path, otherwise filename 'http:' overwrite prefix
                assert self.prefix.path.endswith('/')
                assert not url_part.startswith('/')
                url_part = self.prefix.path + url_part
                self.add_task(
                    urljoin(self.prefix, url_part),
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
                        urljoin(self.prefix, part),
                        reason="from extra_files",
                    )
            else:
                raise ValueError(kind)
        self._add_extra_pages(self.prefix, self.extra_pages)

        # and at the end prepare the saver
        return await self.saver.prepare()

    def start_response(
        self,
        task: Task,
        url: AbsoluteURL,
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

        task.response_headers = Headers(headers)
        task.response_status = status

        status_action = task.response_headers.get('Freezeyt-Action')
        if not status_action:

            # Get a handler for the particular status from configuration
            status_handler = self.status_handlers.get(status[:3])

            if status_handler is None:
                # If a handler for the particular status isn't found,
                # get handler for a group of statuses
                status_handler = self.status_handlers.get(status[0] + 'xx')
            if status_handler is None:
                # Still not found? Use the default handler
                if status.startswith('200'):
                    # default behaviour for status 200
                    status_handler = freezeyt.actions.save
                else:
                    # default behaviour for everything but 200
                    raise UnexpectedStatus(url, status)

            status_action = status_handler(hooks.TaskInfo(task))

        if status_action == 'save':
            return wsgi_write
        elif status_action == 'ignore':
            raise IgnorePage()
        elif status_action == 'follow':
            raise IsARedirect()
        else:
            raise UnexpectedStatus(url, status)


    def _add_extra_pages(
        self,
        prefix: AbsoluteURL,
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
                self._add_extra_pages(prefix, generator(self.user_app))
            elif isinstance(extra, str):
                url = urljoin(prefix, decode_input_path(extra))
                try:
                    self.add_task(
                        url,
                        reason='extra page',
                    )
                except ExternalURLError:
                    raise ExternalURLError(f'External URL specified in extra_pages: {url}')
            else:
                generator = extra
                self._add_extra_pages(prefix, generator(self.user_app))

    async def handle_urls(self) -> None:
        while self.inprogress_tasks:
            # Get an item from self.inprogress_tasks.
            # Since this is a dict, we can't do self.inprogress_tasks[0];
            # and since we don't want to change it we can't use pop().
            # So, start iterating over it, and break the loop immediately
            # when we get the first item.
            for path, task in self.inprogress_tasks.items():
                break
            assert task.asyncio_task is not None
            try:
                await task.asyncio_task
            except Exception as exc:
                task.update_status(TaskStatus.IN_PROGRESS, TaskStatus.FAILED)
                self.call_hook('page_failed', hooks.TaskInfo(task))
                if self.fail_fast:
                    raise exc
            if path in self.inprogress_tasks:
                raise ValueError(f'{task} is in_progress after it was handled')

    @needs_semaphore
    async def handle_one_task(self, task: Task) -> None:
        # Get an URL from the task's set of URLs
        url_parsed = task.get_a_url()
        url = url_parsed

        # url_string should not be needed (except for debug messages)
        url_string = urllib.parse.urlunsplit(url_parsed)

        path_info = url_parsed.path

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

        assert task.response_headers is not None
        finder_name = task.response_headers.get('Freezeyt-URL-Finder')
        if finder_name is not None:
            url_finder = import_variable_from_module(finder_name)
        else:
            content_type = task.response_headers.get('Content-Type')
            mime_type, encoding = parse_options_header(content_type)
            url_finder = self.url_finders.get(mime_type)
        if url_finder is not None:
            with await self.saver.open_filename(task.path) as f:
                finder_result = url_finder(
                    f, url_string, task.response_headers.to_wsgi_list()
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
                    new_url = urljoin(url, link_text)
                    self.add_task(
                        new_url, external_ok=True,
                        reason=f'linked from: {task.path}',
                    )

        if self.config.get('urls_from_link_headers', True):
            for link_header in task.response_headers.getlist('Link'):
                for link in parse_list_header(link_header):
                    link = link.strip()
                    if not link.startswith('<'):
                        raise ValueError(f'Invalid Link header: {link!r}')
                    link_text, sep, rest = link[1:].partition('>')
                    if not sep:
                        raise ValueError(f'Invalid Link header: {link!r}')
                    new_url = urljoin(url, link_text)
                    self.add_task(
                        new_url, external_ok=True,
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
                for task in self.redirecting_tasks.values():
                    raise InfiniteRedirection(task)

    def call_hook(self, hook_name: str, *arguments: Any) -> None:
        for hook in self.hooks.get(hook_name, ()):
            hook(*arguments)
