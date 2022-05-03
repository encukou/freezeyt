import sys
from pathlib import Path, PurePosixPath
from mimetypes import guess_type
import io
import itertools
import json
import functools
import base64
import dataclasses
from typing import Optional, Mapping, Set, List, Dict
import enum
from urllib.parse import urljoin
import asyncio
import inspect
import re

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header
from werkzeug.urls import URL

import freezeyt
from freezeyt.encoding import encode_wsgi_path, decode_input_path
from freezeyt.encoding import encode_file_path
from freezeyt.filesaver import FileSaver
from freezeyt.dictsaver import DictSaver
from freezeyt.util import parse_absolute_url, is_external, add_port
from freezeyt.util import import_variable_from_module
from freezeyt.util import InfiniteRedirection, ExternalURLError
from freezeyt.util import WrongMimetypeError, UnexpectedStatus
from freezeyt.util import UnsupportedSchemeError, MultiError
from freezeyt.compat import asyncio_run, asyncio_create_task
from freezeyt import hooks
from freezeyt.saver import Saver


MAX_RUNNING_TASKS = 100

# HTTP status description for status_handlers:
# 3 digits, or 1 digit and 'xx'.
STATUS_KEY_RE = re.compile('^[0-9]([0-9]{2}|xx)$')


def freeze(app, config):
    return asyncio_run(freeze_async(app, config))


async def freeze_async(app, config):
    freezer = Freezer(app, config)
    try:
        await freezer.prepare()
        freezer.call_hook('start', freezer.freeze_info)
        await freezer.handle_urls()
        await freezer.handle_redirects()
        return await freezer.finish()
    except:
        freezer.cancel_tasks()
        raise


DEFAULT_URL_FINDERS = {
            'text/html': 'get_html_links_async',
            'text/css': 'get_css_links_async'
        }

DEFAULT_STATUS_HANDLERS = {
    '1xx': 'error',
    '200': 'save',
    '2xx': 'error',
    '3xx': 'error',
    '4xx': 'error',
    '5xx': 'error',
}

def mime_db_mimetype(mime_db: dict, url: str) -> Optional[List[str]]:
    """Determines file MIME type from file suffix. Decisions are made
    by mime-db rules.
    """
    suffix = PurePosixPath(url).suffix[1:].lower()

    return mime_db.get(suffix)


def default_mimetype(url: str) -> Optional[List[str]]:
    """Returns file mimetype as a string from mimetype.guess_type.
    file mimetypes are guessed from file suffix.
    """
    file_mimetype, encoding = guess_type(url)
    if file_mimetype is None:
        return None
    else:
        return [file_mimetype]


def check_mimetype(
    url_path, headers,
    default='application/octet-stream', *, get_mimetype=default_mimetype,
):
    """Ensure mimetype sent from headers with file mimetype guessed
    from its suffix.
    Raise WrongMimetypeError if they don't match.
    """
    if url_path.endswith('/'):
        # Directories get saved as index.html
        url_path = 'index.html'
    file_mimetypes = get_mimetype(url_path)
    if file_mimetypes is None:
        file_mimetypes = [default]

    headers = Headers(headers)
    headers_mimetype, encoding = parse_options_header(
        headers.get('Content-Type')
    )

    if isinstance(file_mimetypes, str):
        raise TypeError("get_mimetype result must not be a string")

    if headers_mimetype.lower() not in (m.lower() for m in file_mimetypes):
        raise WrongMimetypeError(file_mimetypes, headers_mimetype, url_path)


def parse_handlers(
    handlers: Mapping, default_module: Optional[str]=None
) -> Mapping:
    result = {}
    for key, handler_or_name in handlers.items():
        if isinstance(handler_or_name, str):
            handler = import_variable_from_module(
                handler_or_name, default_module_name=default_module
            )
        else:
            handler = handler_or_name
        if not callable(handler):
            raise TypeError(
                "Handler for {key!r} in configuration must be a string or a callable,"
                + f" not {type(handler)}!"
            )

        result[key] = handler

    return result


def convert_mime_db(mime_db: Mapping) -> Dict[str, List[str]]:
    """Convert mime-db value 'extensions' to become a key
    and origin mimetype key to dict value as item of list.
    """
    converted_db: Dict[str, List[str]] = {}
    for mimetype, opts in mime_db.items():
        extensions = opts.get('extensions')
        if extensions is not None:
            for extension in extensions:
                mimetypes = converted_db.setdefault(extension.lower(), [])
                mimetypes.append(mimetype.lower())

    return converted_db


def default_url_to_path(path: str) -> str:
    if path.endswith('/') or not path:
        path = path + 'index.html'
    return encode_file_path(path)


def get_path_from_url(prefix: URL, url: URL, url_to_path) -> PurePosixPath:
    if is_external(url, prefix):
        raise ValueError(f'external url {url}')

    path = url.path

    if path.startswith(prefix.path):
        path = path[len(prefix.path):]

    result = url_to_path(path)

    result = PurePosixPath(result)

    if result.is_absolute():
        raise ValueError(
            f"Path may not be absolute: {result}(from {url.to_url()})"
        )
    assert '.' not in result.parts
    if '..' in result.parts:
        raise ValueError(
            f"Path may not contain /../ segment: {result}(from {url.to_url()})"
        )

    return result

class TaskStatus(enum.Enum):
    IN_PROGRESS = "Currently being handled"
    REDIRECTING = "Waiting for target of redirection"
    DONE = "Saved"
    FAILED = "Raised an exception"

@dataclasses.dataclass
class Task:
    path: PurePosixPath
    urls: "Set[URL]"
    freezer: "Freezer"
    response_headers: Optional[Headers] = None
    response_status: Optional[str] = None
    redirects_to: "Optional[Task]" = None
    reasons: set = dataclasses.field(default_factory=set)
    asyncio_task: "Optional[asyncio.Task]" = None

    def __repr__(self):
        return f"<Task for {self.path}, {self.status.name}>"

    def get_a_url(self):
        """Get an arbitrary one of the task's URLs."""
        return next(iter(self.urls))

    @property
    def status(self):
        for status, queue in self.freezer.task_queues.items():
            if self.path in queue:
                return status
        raise ValueError(f'Task not registered with freezer: {self}')

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

class Freezer:
    saver: Saver

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.check_version(self.config.get('version'))

        self.freeze_info = hooks.FreezeInfo(self)

        CONFIG_DATA = (
            ('extra_pages', ()),
            ('extra_files', None),
            ('default_mimetype', 'application/octet-stream'),
            ('get_mimetype', default_mimetype),
            ('mime_db_file', None),
            ('url_to_path', default_url_to_path)
        )
        for attr_name, default in CONFIG_DATA:
            setattr(self, attr_name, config.get(attr_name, default))

        if self.mime_db_file:
            with open(self.mime_db_file) as file:
                mime_db = json.load(file)

            mime_db = convert_mime_db(mime_db)
            self.get_mimetype = functools.partial(mime_db_mimetype, mime_db)

        if isinstance(self.get_mimetype, str):
            self.get_mimetype = import_variable_from_module(self.get_mimetype)

        if isinstance(self.url_to_path, str):
            self.url_to_path = import_variable_from_module(self.url_to_path)

        if config.get('use_default_url_finders', True):
            _url_finders = dict(
                DEFAULT_URL_FINDERS, **config.get('url_finders', {})
            )
        else:
            _url_finders = config.get('url_finders', {})

        self.url_finders = parse_handlers(
            _url_finders, default_module='freezeyt.url_finders'
        )

        _status_handlers = dict(
            DEFAULT_STATUS_HANDLERS, **config.get('status_handlers', {})
        )
        self.status_handlers = parse_handlers(
            _status_handlers, default_module='freezeyt.status_handlers'
        )
        for key in self.status_handlers:
            if not STATUS_KEY_RE.fullmatch(key):
                raise ValueError(
                    'Status descriptions must be strings with 3 digits or one '
                    + f'digit and "xx", got f{key!r}'
                )

        prefix = config.get('prefix', 'http://localhost:8000/')

        # Decode path in the prefix URL.
        # Save the parsed version of prefix as self.prefix
        prefix_parsed = parse_absolute_url(prefix)
        decoded_path = decode_input_path(prefix_parsed.path)
        if not decoded_path.endswith('/'):
            raise ValueError('prefix must end with /')
        self.prefix = prefix_parsed.replace(path=decoded_path)

        output = config['output']
        if isinstance(output, str):
            output = {'type': 'dir', 'dir': output}

        if output['type'] == 'dict':
            self.saver = DictSaver(self.prefix)
        elif output['type'] == 'dir':
            try:
                output_dir = output['dir']
            except KeyError:
                raise ValueError("output directory not specified")
            self.saver = FileSaver(Path(output_dir), self.prefix)
        else:
            raise ValueError(f"unknown output type {output['type']}")

        # The tasks for individual pages are tracked in the followng sets
        # (actually dictionaries: {task.path: task})
        # Each task must be in exactly in one of these.
        self.done_tasks = {}
        self.redirecting_tasks = {}
        self.inprogress_tasks = {}
        self.failed_tasks = {}
        self.task_queues = {
            TaskStatus.DONE: self.done_tasks,
            TaskStatus.REDIRECTING: self.redirecting_tasks,
            TaskStatus.IN_PROGRESS: self.inprogress_tasks,
            TaskStatus.FAILED: self.failed_tasks,
        }

        try:
            self.add_task(prefix_parsed, reason='site root (homepage)')
            self._add_extra_files()
            self._add_extra_pages(prefix, self.extra_pages)

            self.hooks = {}
            for name, funcs in config.get('hooks', {}).items():
                for func in funcs:
                    if isinstance(func, str):
                        func = import_variable_from_module(func)
                    self.add_hook(name, func)

            for plugin in config.get('plugins', {}):
                if isinstance(plugin, str):
                    plugin = import_variable_from_module(plugin)
                plugin(self.freeze_info)

            self.semaphore = asyncio.Semaphore(MAX_RUNNING_TASKS)
        except:
            self.cancel_tasks()
            raise

    def check_version(self, config_version):
        if config_version is None:
            return
        if not isinstance(config_version, float):
            main_version = str(config_version).split(".")[0]
        else:
            raise VersionMismatch("The specified version has to be string or int i.e. 1, 1.1 or '1', '1.1'.")

        current_version = freezeyt.__version__.split(".")[0]
        if main_version != current_version:
            raise VersionMismatch("The specified version does not match the freezeyt main version.")

    def add_hook(self, hook_name, func):
        self.hooks.setdefault(hook_name, []).append(func)

    def cancel_tasks(self):
        for task in self.inprogress_tasks.values():
            task.asyncio_task.cancel()

    async def finish(self):
        success = not self.failed_tasks
        cleanup = self.config.get("cleanup", True)
        result = await self.saver.finish(success, cleanup)
        if success:
            return result
        raise MultiError(self.failed_tasks.values())

    def add_static_task(
        self, url: URL, content: bytes, *, external_ok: bool = False,
        reason: str = None,
    ) -> Optional[Task]:
        """Add a task to save the given content at the given URL.

        If no task is added (e.g. for external URLs), return None.
        """
        task = self._add_task(url, external_ok=external_ok, reason=reason)
        if task and task.asyncio_task is None:
            coroutine = self.handle_content_task(task, content)
            task.asyncio_task = asyncio_create_task(coroutine, name=task.path)
        return task

    def add_task(
        self, url: URL, *, external_ok: bool = False, reason: str = None,
    ) -> Optional[Task]:
        """Add a task to freeze the given URL

        If no task is added (e.g. for external URLs), return None.
        """
        task = self._add_task(url, external_ok=external_ok, reason=reason)
        if task and task.asyncio_task is None:
            coroutine = self.handle_one_task(task)
            task.asyncio_task = asyncio_create_task(coroutine, name=task.path)
        return task

    def _add_task(
        self, url: URL, *, external_ok: bool = False, reason: str = None,
    ) -> Optional[Task]:
        if is_external(url, self.prefix):
            if external_ok:
                return None
            raise ExternalURLError(f'Unexpected external URL: {url}')

        path = get_path_from_url(self.prefix, url, self.url_to_path)

        for queue in self.task_queues.values():
            if path in queue:
                task = queue[path]
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

    def _add_extra_files(self):
        if self.extra_files is not None:
            for url_part, content in self.extra_files.items():
                if isinstance(content, str):
                    content = content.encode()
                elif isinstance(content, dict):
                    if 'base64' in content:
                        content = base64.b64decode(content['base64'])
                    elif 'copy_from' in content:
                        path = Path(content['copy_from'])
                        self.freeze_extra_files_from_path(
                            url_path=PurePosixPath(url_part),
                            disk_path=path,
                        )
                        continue
                    else:
                        raise ValueError(
                            'a mapping in extra_files must contain '
                            + '"base64" or "copy_from"'
                        )
                url = self.prefix.join(url_part)
                self.add_static_task(
                    url=url, reason="from extra_files", content=content,
                )

    def freeze_extra_files_from_path(self, url_path, disk_path):
        if disk_path.is_dir():
            for subpath in disk_path.iterdir():
                self.freeze_extra_files_from_path(
                    url_path / subpath.name, subpath)
        else:
            url = self.prefix.join(str(url_path))
            self.add_static_task(
                url=url,
                reason="from extra_files",
                content=disk_path.read_bytes(),
            )


    async def prepare(self):
        await self.saver.prepare()

    def start_response(
        self, task, url, wsgi_write, status, headers, exc_info=None,
    ):
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

        if self.status_handlers.get(status[:3]):
            status_handler = self.status_handlers.get(status[:3])
        elif self.status_handlers.get(status[0] + 'xx'):
            status_handler = self.status_handlers.get(status[0] + 'xx')
        else:
            raise UnexpectedStatus(url, status)

        task.response_headers = Headers(headers)
        task.response_status = status

        status_action = status_handler(hooks.TaskInfo(task))

        if status_action == 'save':
            check_mimetype(
                url.path, headers,
                default=self.default_mimetype,
                get_mimetype=self.get_mimetype
            )
            return wsgi_write
        elif status_action == 'ignore':
            raise IgnorePage()
        elif status_action == 'follow':
            raise IsARedirect()
        else:
            raise UnexpectedStatus(url, status)


    def _add_extra_pages(self, prefix, extras):
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
                self._add_extra_pages(prefix, generator(self.app))
            elif isinstance(extra, str):
                url = parse_absolute_url(urljoin(prefix, decode_input_path(extra)))
                try:
                    self.add_task(
                        url,
                        reason='extra page',
                    )
                except ExternalURLError:
                    raise ExternalURLError(f'External URL specified in extra_pages: {url}')
            else:
                generator = extra
                self._add_extra_pages(prefix, generator(self.app))

    async def handle_urls(self):
        while self.inprogress_tasks:
            # Get an item from self.inprogress_tasks.
            # Since this is a dict, we can't do self.inprogress_tasks[0];
            # and since we don't want to change it we can't use pop().
            # So, start iterating over it, and break the loop immediately
            # when we get the first item.
            for path, task in self.inprogress_tasks.items():
                break
            try:
                await task.asyncio_task
            except Exception:
                del self.inprogress_tasks[task.path]
                self.failed_tasks[task.path] = task
                self.call_hook('page_failed', hooks.TaskInfo(task))
            if path in self.inprogress_tasks:
                raise ValueError(f'{task} is in_progress after it was handled')

    @needs_semaphore
    async def handle_content_task(self, task, content):
        await self.saver.save_to_filename(task.path, [content])
        del self.inprogress_tasks[task.path]
        self.done_tasks[task.path] = task
        self.call_hook('page_frozen', hooks.TaskInfo(task))

    @needs_semaphore
    async def handle_one_task(self, task):
        # Get an URL from the task's set of URLs
        url_parsed = task.get_a_url()
        url = url_parsed

        # url_string should not be needed (except for debug messages)
        url_string = url_parsed.to_url()

        path_info = url_parsed.path

        if path_info.startswith(self.prefix.path):
            path_info = "/" + path_info[len(self.prefix.path):]

        environ = {
            'SERVER_NAME': self.prefix.ascii_host,
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
        wsgi_write_data = []
        start_response = functools.partial(
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
            del self.inprogress_tasks[task.path]
            self.done_tasks[task.path] = task
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
            try:
                close = result_iterable.close
            except AttributeError:
                pass
            else:
                close()

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
                for new_url_text in links:
                    new_url = url.join(decode_input_path(new_url_text))
                    try:
                        new_url = add_port(new_url)
                    except UnsupportedSchemeError:
                        # If this has a scheme other than http and https,
                        # it's an external url and we don't follow it.
                        pass
                    else:
                        self.add_task(
                            new_url, external_ok=True,
                            reason=f'linked from: {task.path}',
                        )

        del self.inprogress_tasks[task.path]
        self.done_tasks[task.path] = task

        self.call_hook('page_frozen', hooks.TaskInfo(task))

    @needs_semaphore
    async def handle_redirects(self):
        """Save copies of target pages for redirect_policy='follow'"""
        while self.redirecting_tasks:
            saved_something = False
            for key, task in list(self.redirecting_tasks.items()):
                if task.redirects_to.status == TaskStatus.FAILED:
                    # Don't process redirects to a failed pages
                    del self.redirecting_tasks[key]
                    self.done_tasks[task.path] = task
                    continue
                if task.redirects_to.status != TaskStatus.DONE:
                    continue

                with await self.saver.open_filename(task.redirects_to.path) as f:
                    await self.saver.save_to_filename(task.path, f)
                self.call_hook('page_frozen', hooks.TaskInfo(task))
                del self.redirecting_tasks[key]
                self.done_tasks[task.path] = task
                saved_something = True
            if not saved_something:
                # Get some task (the first one we get by iteration) for the
                # error message.
                for task in self.redirecting_tasks.values():
                    raise InfiniteRedirection(task)

    def call_hook(self, hook_name, *arguments):
        for hook in self.hooks.get(hook_name, ()):
            hook(*arguments)
