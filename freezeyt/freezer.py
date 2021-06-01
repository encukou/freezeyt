import sys
from pathlib import Path, PurePosixPath
from mimetypes import guess_type
import io
import itertools
import functools
import base64
import dataclasses
from typing import Optional
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
from freezeyt.getlinks_html import get_all_links
from freezeyt.getlinks_css import get_links_from_css
from freezeyt import hooks


def freeze(app, config):
    freezer = Freezer(app, config)
    freezer.prepare()

    hook = freezer.hooks.get('start')
    if hook:
        hook(freezer.freeze_info)

    freezer.freeze_extra_files()
    freezer.handle_urls()
    freezer.handle_redirects()
    return freezer.get_result()


def check_mimetype(url_path, headers, default='application/octet-stream'):
    if url_path.endswith('/'):
        # Directories get saved as index.html
        url_path = 'index.html'
    f_type, f_encode = guess_type(url_path)
    if not f_type:
        f_type = default
    headers = Headers(headers)
    cont_type, cont_encode = parse_options_header(headers.get('Content-Type'))
    if f_type.lower() != cont_type.lower():
        raise ValueError(
            f"Content-type '{cont_type}' is different from filetype '{f_type}'"
            + f" guessed from '{url_path}'"
        )


def url_to_path(prefix, parsed_url):
    if is_external(parsed_url, prefix):
        raise ValueError(f'external url {parsed_url}')

    url_path = parsed_url.path

    if url_path.startswith(prefix.path):
        url_path = url_path[len(prefix.path):]

    if url_path.endswith('/') or not url_path:
        url_path = url_path + 'index.html'

    result = PurePosixPath(encode_file_path(url_path))

    assert not result.is_absolute(), result
    assert '.' not in result.parts
    if '..' in result.parts:
        raise ValueError(
            f"URL may not contain /../ segment: {parsed_url.to_url()}"
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
    redirect: "Task" = None
    response_headers: Headers = None
    redirects_to: "Task" = None
    status: TaskStatus = TaskStatus.PENDING

    def __repr__(self):
        return f"<Task for {self.path}, {self.status.name}>"

    def get_a_url(self):
        """Get an arbitrary one of the task's URLs."""
        return next(iter(self.urls))

class IsARedirect(BaseException):
    """Raised when a page redirects and freezing it should be postponed"""

class Freezer:
    def __init__(self, app, config):
        self.app = app
        self.config = config

        self.freeze_info = hooks.FreezeInfo(self)

        self.extra_pages = config.get('extra_pages', ())
        self.extra_files = config.get('extra_files', None)

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

        self.done_tasks = {}
        self.redirecting_tasks = {}

        self.pending_tasks = {}
        self.add_task(prefix_parsed)
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

    def add_task(self, url: URL, *, external_ok: bool = False) -> Optional[Task]:
        """Add a task to freeze the given URL

        If no task is added (e.g. for external URLs), return None.
        """
        if is_external(url, self.prefix):
            if external_ok:
                return None
            raise ExternalURLError(f'Unexpected external URL: {url}')

        path = url_to_path(self.prefix, url)

        if path in self.pending_tasks:
            task = self.pending_tasks[path]
            task.urls.add(url)
            return task
        elif path in self.done_tasks:
            task = self.done_tasks[path]
            task.urls.add(url)
            return task
        else:
            task = Task(path, {url})
            self.pending_tasks[path] = task
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
            print(f"Redirect {url.to_url()} to {location}")
            redirect_policy = self.config.get('redirect_policy', 'error')
            if redirect_policy == 'save':
                status = "200"
            elif redirect_policy == 'follow':
                location = add_port(url.join(location))
                target_task = self.add_task(location, external_ok=True)
                task.redirects_to = target_task
                self.redirecting_tasks[task.path] = task
                raise IsARedirect()
            elif redirect_policy == 'error':
                # handled below
                pass
            else:
                raise ValueError(
                    f'redirect policy {redirect_policy} not supported'
                )
        if not status.startswith("200"):
            raise ValueError(f"Found broken link: {url.to_url()}, status {status}")
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
                generator = extra['generator']
                if isinstance(generator, str):
                    generator = import_variable_from_module(generator)
                self._add_extra_pages(prefix, generator(self.app))
            elif isinstance(extra, str):
                url = parse_absolute_url(urljoin(prefix, decode_input_path(extra)))
                try:
                    self.add_task(url)
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

            print('task:', task)
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

            with self.saver.open_filename(task.path) as f:
                cont_type, cont_encode = parse_options_header(task.response_headers.get('Content-Type'))
                if cont_type == "text/html":
                    links = get_all_links(f, url_string, task.response_headers)
                    for new_url in links:
                        self.add_task(parse_absolute_url(new_url), external_ok=True)
                elif cont_type == "text/css":
                    for new_url in get_links_from_css(f, url_string):
                        self.add_task(parse_absolute_url(new_url), external_ok=True)

            task.status = TaskStatus.DONE

            hook = self.hooks.get('page_frozen')
            if hook:
                hook(hooks.TaskInfo(task, self))

    def handle_redirects(self):
        """Save copies of target pages for redirect_policy='follow'"""
        print('handle_redirects', self.redirecting_tasks)
        for task in self.redirecting_tasks.values():
            if task.redirects_to.status != TaskStatus.DONE:
                raise InfiniteRedirection(
                    f'{task.get_a_url()} redirects to {task.redirects_to.get_a_url()}, which was not frozen (most likely because of infinite redirection)'
                )
            with self.saver.open_filename(task.redirects_to.path) as f:
                self.saver.save_to_filename(task.path, f)
