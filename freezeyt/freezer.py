import sys
from pathlib import Path
from mimetypes import guess_type

from urllib.parse import urlparse, urljoin
from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header

from freezeyt.encoding import decode_input_path, encode_wsgi_path
from freezeyt.filesaver import FileSaver
from freezeyt.util import parse_absolute_url, is_external
from freezeyt.getlinks_html import get_all_links
from freezeyt.getlinks_css import get_links_from_css


def freeze(app, path, config):
    freezer = Freezer(app, path, config)
    freezer.freeze_extra_files()
    freezer.handle_urls()


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
    def __init__(self, app, path, config):
        self.app = app
        self.path = Path(path)
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
        self.prefix = prefix_parsed._replace(path=decoded_path)

        self.saver = FileSaver(self.path, self.prefix)

    def freeze_extra_files(self):
        if self.extra_files is not None:
            for filename, content in self.extra_files.items():
                filename = self.path / filename
                filename.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, bytes):
                    filename.write_bytes(content)
                else:
                    filename.write_text(content)


    def start_response(self, status, headers):
        if not status.startswith("200"):
            raise ValueError("Found broken link.")
        else:
            print('status', status)
            print('headers', headers)
            check_mimetype(urlparse(self.url).path, headers)
            self.response_headers = Headers(headers)

    def handle_urls(self):
        prefix = self.prefix.geturl()
        new_urls = [prefix]
        for extra in self.extra_pages:
            new_urls.append(urljoin(prefix, decode_input_path(extra)))

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
                'SERVER_NAME': self.prefix.hostname,
                'SERVER_PORT': str(self.prefix.port),
                'REQUEST_METHOD': 'GET',
                'PATH_INFO': encode_wsgi_path(path_info),
                'SCRIPT_NAME': encode_wsgi_path(self.prefix.path),
                'SERVER_PROTOCOL': 'HTTP/1.1',

                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'http',
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False,

                'freezeyt.freezing': True,
            }

            result = self.app(environ, self.start_response)

            self.saver.save(url_parsed, result)

            with self.saver.open(url_parsed) as f:
                cont_type, cont_encode = parse_options_header(self.response_headers.get('Content-Type'))
                if cont_type == "text/html":
                    new_urls.extend(get_all_links(f, url, self.response_headers))
                elif cont_type == "text/css":
                    new_urls.extend(get_links_from_css(f, url))
                else:
                    continue
