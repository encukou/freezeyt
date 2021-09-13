import sys
from pathlib import Path, PurePosixPath
from mimetypes import guess_type
import io
import itertools
import functools
import base64
import dataclasses
from typing import Optional, Mapping
import enum
from urllib.parse import urljoin

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header
from werkzeug.urls import URL

from freezeyt.encoding import encode_wsgi_path, decode_input_path
from freezeyt.encoding import encode_file_path
from freezeyt.filesaver import FileSaver
from freezeyt.dictsaver import DictSaver
from freezeyt.util import parse_absolute_url, is_external, add_port
from freezeyt.util import import_variable_from_module
from freezeyt.util import InfiniteRedirection, ExternalURLError
from freezeyt.util import UnexpectedStatus, WrongMimetypeError
from freezeyt.util import UnsupportedSchemeError
from freezeyt import hooks


def freeze(app, config):
    freezer = Freezer(app, config)
    freezer.prepare()
    freezer.call_hook('start', freezer.freeze_info)
    freezer.freeze_extra_files()
    freezer.handle_urls()
    freezer.handle_redirects()
    return freezer.get_result()


DEFAULT_URL_FINDERS = {
            'text/html': 'get_html_links',
            'text/css': 'get_css_links'
        }


def check_mimetype(url_path, headers, default='application/octet-stream'):
    if url_path.endswith('/'):
        # Directories get saved as index.html
        url_path = 'index.html'
    file_type, file_encoding = guess_type(url_path)
    if not file_type:
        file_type = default
    headers = Headers(headers)
    mime_type, encoding = parse_options_header(headers.get('Content-Type'))
    if file_type.lower() != mime_type.lower():
        raise WrongMimetypeError(file_type, mime_type, url_path)


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


def default_url_to_path(path):
    if path.endswith('/') or not path:
        path = path + 'index.html'
    return encode_file_path(path)


def get_path_from_url(prefix, url, url_to_path):
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
    PENDING = "Not started"
    REQUESTED = "Currently being handled"
    DONE = "Saved"

@dataclasses.dataclass
class Task:
    path: Path
    urls: "set[URL]"
    response_headers: Optional[Headers] = None
    redirects_to: "Optional[Task]" = None
    status: TaskStatus = TaskStatus.PENDING
    reasons: set = dataclasses.field(default_factory=set)

    def __repr__(self):
        return f"<Task for {self.path}, {self.status.name}>"

    def get_a_url(self):
        """Get an arbitrary one of the task's URLs."""
        return next(iter(self.urls))

class IsARedirect(BaseException):
    """Raised when a page redirects and freezing it should be postponed"""

class IgnorePage(BaseException):
    """Raised when freezing a page should be ignored"""

class Freezer:
    def __init__(self, app, config):
        self.app = app
        self.config = config

        self.freeze_info = hooks.FreezeInfo(self)

        self.extra_pages = config.get('extra_pages', ())
        self.extra_files = config.get('extra_files', None)

        self.url_finders = parse_handlers(
                                config.get('url_finders', DEFAULT_URL_FINDERS),
                                default_module='freezeyt.url_finders'
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

        self.url_to_path = config.get('url_to_path', default_url_to_path)
        if isinstance(self.url_to_path, str):
            self.url_to_path = import_variable_from_module(self.url_to_path)

        self.done_tasks = {}
        self.redirecting_tasks = {}

        self.pending_tasks = {}
        self.add_task(prefix_parsed, reason='site root (homepage)')
        self._add_extra_pages(prefix, self.extra_pages)

        self.hooks = {}
        for name, func in config.get('hooks', {}).items():
            if isinstance(func, str):
                func = import_variable_from_module(func)
            self.hooks[name] = func


    def get_result(self):
        get_result = getattr(self.saver, 'get_result', None)
        if get_result is not None:
            return self.saver.get_result()

    def add_task(self, url: URL, *, external_ok: bool = False, reason: str = None) -> Optional[Task]:
        """Add a task to freeze the given URL

        If no task is added (e.g. for external URLs), return None.
        """
        if is_external(url, self.prefix):
            if external_ok:
                return None
            raise ExternalURLError(f'Unexpected external URL: {url}')

        path = get_path_from_url(self.prefix, url, self.url_to_path)

        if path in self.pending_tasks:
            task = self.pending_tasks[path]
            task.urls.add(url)
        elif path in self.done_tasks:
            task = self.done_tasks[path]
            task.urls.add(url)
        else:
            task = Task(path, {url})
            self.pending_tasks[path] = task
        if reason:
            task.reasons.add(reason)
        return task

    def freeze_extra_files(self):
        if self.extra_files is not None:
            for filename, content in self.extra_files.items():
                if isinstance(content, str):
                    content = content.encode()
                elif isinstance(content, dict):
                    if 'base64' in content:
                        content = base64.b64decode(content['base64'])
                    elif 'copy_from' in content:
                        content = Path(content['copy_from']).read_bytes()
                    else:
                        raise ValueError(
                            'a mapping in extra_files must contain '
                            + '"base64" or "copy_from"'
                        )
                self.saver.save_to_filename(filename, [content])

    def prepare(self):
        self.saver.prepare()

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

        task.response_headers = Headers(headers)
        if status.startswith("3"):
            location = task.response_headers['Location']
            redirect_policy = self.config.get('redirect_policy', 'error')
            if redirect_policy == 'save':
                status = "200"
            elif redirect_policy == 'follow':
                location = add_port(url.join(location))
                target_task = self.add_task(
                    location,
                    external_ok=True,
                    reason=f'target of redirect from {url}',
                )
                task.redirects_to = target_task
                self.redirecting_tasks[task.path] = task
                raise IsARedirect()
            elif redirect_policy == 'ignore':
                raise IgnorePage()
            elif redirect_policy == 'error':
                raise UnexpectedStatus(url, status, task.reasons)
            else:
                raise ValueError(
                    f'redirect policy {redirect_policy} not supported'
                )
        if not status.startswith("200"):
            raise UnexpectedStatus(url, status, task.reasons)
        else:
            check_mimetype(
                url.path, headers,
                default=self.config.get(
                    'default_mimetype', 'application/octet-stream',
                ),
            )
        return wsgi_write

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

    def handle_urls(self):
        while self.pending_tasks:
            file_path, task = self.pending_tasks.popitem()

            # Get an URL from the task's set of URLs
            url_parsed = task.get_a_url()
            url = url_parsed

            # url_string should not be needed (except for debug messages)
            url_string = url_parsed.to_url()

            if task.path in self.done_tasks:
                continue

            self.done_tasks[task.path] = task

            task.status = TaskStatus.REQUESTED

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
                'SERVER_SOFTWARE': 'freezeyt/0.1',

                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'http',
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
            # must be doneas part of this call.
            try:
                result_iterable = self.app(environ, start_response)
            except IsARedirect:
                continue
            except IgnorePage:
                continue

            # Combine the list of data from write() with the returned
            # iterable object.
            full_result = itertools.chain(
                wsgi_write_data,
                result_iterable,
            )

            self.saver.save_to_filename(task.path, full_result)

            try:
                close = result_iterable.close
            except AttributeError:
                pass
            else:
                close()

            with self.saver.open_filename(file_path) as f:
                content_type = task.response_headers.get('Content-Type')
                mime_type, encoding = parse_options_header(content_type)
                url_finder = self.url_finders.get(mime_type)
                if url_finder is not None:
                    links = url_finder(
                        f, url_string, task.response_headers.to_wsgi_list()
                    )
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
                                reason=f'linked from {url}',
                            )

            task.status = TaskStatus.DONE

            self.call_hook('page_frozen', hooks.TaskInfo(task, self))

    def handle_redirects(self):
        """Save copies of target pages for redirect_policy='follow'"""
        for task in self.redirecting_tasks.values():
            if task.redirects_to.status != TaskStatus.DONE:
                raise InfiniteRedirection(task)

            with self.saver.open_filename(task.redirects_to.path) as f:
                self.saver.save_to_filename(task.path, f)
            self.call_hook('page_frozen', hooks.TaskInfo(task, self))

    def call_hook(self, hook_name, *arguments):
        hook = self.hooks.get(hook_name)
        if hook:
            hook(*arguments)
