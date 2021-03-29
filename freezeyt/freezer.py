import sys
from pathlib import Path
from mimetypes import guess_type
import io
import itertools
import functools
import base64

from urllib.parse import urljoin
from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header
from werkzeug.urls import url_parse

from freezeyt.encoding import encode_wsgi_path, decode_input_path
from freezeyt.filesaver import FileSaver
from freezeyt.dictsaver import DictSaver
from freezeyt.util import parse_absolute_url, is_external
from freezeyt.util import import_variable_from_module
from freezeyt.getlinks_html import get_all_links
from freezeyt.getlinks_css import get_links_from_css


def freeze(app, config):
    freezer = Freezer(app, config)
    freezer.prepare()
    freezer.freeze_extra_files()
    freezer.handle_urls()
    return freezer.get_result()


def check_mimetype(url_path, headers):
    if url_path.endswith('/'):
        # Directories get saved as index.html
        url_path = 'index.html'
    f_type, f_encode = guess_type(url_path)
    if not f_type:
        f_type = 'application/octet-stream'
    headers = Headers(headers)
    cont_type, cont_encode = parse_options_header(headers.get('Content-Type'))
    if f_type.lower() != cont_type.lower():
        raise ValueError(
            f"Content-type '{cont_type}' is different from filetype '{f_type}'"
            + f" guessed from '{url_path}'"
        )


class Freezer:
    def __init__(self, app, config):
        self.app = app
        self.config = config

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
            output = {'type': output}

        if output['type'] == 'dict':
            self.saver = DictSaver(self.prefix)
        else:
            self.saver = FileSaver(Path(output['dir']), self.prefix)

    def get_result(self):
        get_result = getattr(self.saver, 'get_result', None)
        if get_result is not None:
            return self.saver.get_result()

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
        self, wsgi_write, status, headers, exc_info=None,
    ):
        """WSGI start_response hook

        The application we are freezing will call this method
        and supply the status, headers, exc_info arguments.
        (self and wsgi_write are provided by freezeyt.)

        See: https://www.python.org/dev/peps/pep-3333/#the-start-response-callable

        Arguments:
            wsgi_write: function that the application can call to output data
            status: HTTP status line, like '200 OK'
            headers: Dict of HTTP headers
            exc_info: Information about a server error, if any.
                Will be raised if given.
        """
        if exc_info:
            exc_type, value, traceback = exc_info
            if value is not None:
                raise value
        if not status.startswith("200"):
            raise ValueError(f"Found broken link. URL - {self.url}, STATUS - {status}")
        else:
            print('status', status)
            print('headers', headers)
            check_mimetype(url_parse(self.url).path, headers)
            self.response_headers = Headers(headers)
        return wsgi_write

    def _add_extra_pages(self, urls, prefix, extras):
        """Add URLs of extra pages from config.

        Handles both literal URLs and generators.
        """
        for extra in extras:
            if isinstance(extra, dict):
                generator = extra['generator']
                if isinstance(generator, str):
                    generator = import_variable_from_module(generator)
                self._add_extra_pages(urls, prefix, generator(self.app))
            elif isinstance(extra, str):
                urls.append(urljoin(prefix, decode_input_path(extra)))
            else:
                generator = extra
                self._add_extra_pages(urls, prefix, generator(self.app))

    def handle_urls(self):
        prefix = self.prefix.to_url()
        new_urls = [prefix]
        self._add_extra_pages(new_urls, prefix, self.extra_pages)

        visited_urls = set()

        while new_urls:
            url = new_urls.pop()
            self.url = url

            if url in visited_urls:
                continue

            visited_urls.add(url)

            url_parsed = parse_absolute_url(url)

            if is_external(url_parsed, self.prefix):
                print('skipping external', url)
                continue

            print('link:', url)

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
                wsgi_write_data.append,
            )

            # Call the application. All calls to write (wsgi_write_data.append)
            # must be doneas part of this call.
            result_iterable = self.app(environ, start_response)

            # Combine the list of data from write() with the returned
            # iterable object.
            full_result = itertools.chain(
                wsgi_write_data,
                result_iterable,
            )

            self.saver.save(url_parsed, full_result)

            try:
                close = result_iterable.close
            except AttributeError:
                pass
            else:
                close()

            with self.saver.open(url_parsed) as f:
                cont_type, cont_encode = parse_options_header(self.response_headers.get('Content-Type'))
                if cont_type == "text/html":
                    new_urls.extend(get_all_links(f, url, self.response_headers))
                elif cont_type == "text/css":
                    new_urls.extend(get_links_from_css(f, url))
                else:
                    continue
