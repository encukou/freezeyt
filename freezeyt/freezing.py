from urllib.parse import urlparse, urljoin
from pathlib import Path
from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header
from mimetypes import guess_type
import xml.dom.minidom
import sys
import html5lib
import cssutils

from freezeyt.encoding import decode_input_path, encode_wsgi_path
from freezeyt.encoding import encode_file_path


def parse_absolute_url(url):
    """Parse absolute URL

    Returns the same result as urllib.parse.urlparse, but works on
    absolute HTTP and HTTPS URLs only.
    The result port is always an integer.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Need an absolute URL")

    if parsed.scheme not in ('http', 'https'):
        raise ValueError("URL scheme must be http or https")

    if parsed.port == None:
        if parsed.scheme == 'http':
            parsed = parsed._replace(netloc=parsed.hostname + ':80')
        elif parsed.scheme == 'https':
            parsed = parsed._replace(netloc=parsed.hostname + ':443')
        else:
            raise ValueError("URL scheme must be http or https")

    return parsed


def url_to_filename(base, url, hostname='localhost', port=8000, path='/'):
    """Return the filename to which the page is frozen.

    Parameters:
    base - Filesystem base path (eg. /tmp/)
    url - Absolute URL (eg. http://example.com:8000/foo/second.html) to create filename
    hostname - Domain name from URL to deploy web app in production (eg. 'example.com')
    port - HTTP port number from URL to deploy web app in production (eg. 8000)
    path - URL path from URL to deploy web app in production (eg. '/foo/second.html')
    """
    url_parse = parse_absolute_url(url)

    if url_parse.hostname == hostname and url_parse.port == port:
        url_path = url_parse.path
    else:
        raise ValueError(f"Got external URL:{url}\
                                    instead of {hostname}:{port}")

    if url_path.startswith(path):
        url_path = '/' + url_path[len(path):]

    if url_path.endswith('/'):
        url_path = url_path + 'index.html'

    return base / encode_file_path(url_path).lstrip('/')


def freeze(app, path, config):
    """Freeze (create files of) all pages from a WSGI server.

    Parameters:
    app -- web app you want to freeze
    path -- path to the file
    prefix (url) -- URL to deploy web app
    extra_pages -- pages without any link in application
    extra_files -- files dont generate by app but needs to correct deploy
    """
    path = Path(path)
    prefix = config.get('prefix', 'http://localhost:8000/')
    extra_pages = config.get('extra_pages', ())
    extra_files = config.get('extra_files', None)

    # Decode path in the prefix URL.
    # Both "prefix" and "prefix_parsed" will have the path decoded.
    prefix_parsed = parse_absolute_url(prefix)
    decoded_path = decode_input_path(prefix_parsed.path)
    prefix_parsed = prefix_parsed._replace(path=decoded_path)
    prefix = prefix_parsed.geturl()

    hostname = prefix_parsed.hostname
    port = prefix_parsed.port
    script_name = prefix_parsed.path

    if extra_files is not None:
        for filename, content in extra_files.items():
            filename = path / filename
            filename.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                filename.write_bytes(content)
            else:
                filename.write_text(content)

    def start_response(status, headers):

        # The rest of the program will need to know the response
        # headers, so we need to pass them out of this function somehow.
        # Just assigning to a variable would create a local variable, which
        # would disappear when start_response() ends.
        # To prevent that, we use `nonlocal` to say we want to set the variable
        # from the enclosing function, freeze().
        nonlocal response_headers

        if not status.startswith("200"):
            raise ValueError("Found broken link.")
        else:
            print('status', status)
            print('headers', headers)
            check_mimetype(filename, headers)
            response_headers = Headers(headers)

    new_urls = [prefix]
    for extra in extra_pages:
        new_urls.append(urljoin(prefix, decode_input_path(extra)))

    visited_urls = set()

    while new_urls:
        url = new_urls.pop()

        # url = http://freezeyt.test:1234/foo/čau/

        if url in visited_urls:
            continue

        visited_urls.add(url)

        try:
            filename = url_to_filename(path, url,
                                        hostname=hostname,
                                        port=port,
                                        path=script_name)
        except ValueError as err:
            print(err)
            print('skipping', url)
            continue

        print('link:', url)

        path_info = urlparse(url).path

        if path_info.startswith(script_name):
            path_info = "/" + path_info[len(script_name):]

        print('path_info:', path_info)

        environ = {
            'SERVER_NAME': hostname,
            'SERVER_PORT': str(port),
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': encode_wsgi_path(path_info),
            'SCRIPT_NAME': encode_wsgi_path(script_name),
            'SERVER_PROTOCOL': 'HTTP/1.1',

            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,

            'freezeyt.freezing': True,
        }

        # app() will call start_response(), which will set
        # `response_headers` to a Headers object.
        response_headers = None

        result = app(environ, start_response)

        print(f'Saving to {filename}')

        filename.parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "wb") as f:
            for item in result:
                f.write(item)

        with open(filename, "rb") as f:
            cont_type, cont_encode = parse_options_header(response_headers.get('Content-Type'))
            if cont_type == "text/html":
                new_urls.extend(get_all_links(f, url, response_headers))
            elif cont_type == "text/css":
                new_urls.extend(get_links_from_css(f, url))
            else:
                continue


def get_all_links(
    page_content: bytes, base_url, headers: Headers = None
) -> list:
    """Get all links from "page_content".

    Return an iterable of strings.

    base_url is the URL of the page.
    """
    if headers == None:
        cont_charset = None
    else:
        content_type_header = headers.get('Content-Type')
        cont_type, cont_options = parse_options_header(content_type_header)
        cont_charset = cont_options.get('charset')
    document = html5lib.parse(page_content, transport_encoding=cont_charset)
    return get_links_from_node(document, base_url)


def get_links_from_node(node: xml.dom.minidom.Node, base_url) -> list:
    """Get all links from xml.dom.minidom Node."""
    result = []
    if 'href' in node.attrib:
        href = decode_input_path(node.attrib['href'])
        full_url = urljoin(base_url, href)
        result.append(full_url)
    if 'src' in node.attrib:
        href = decode_input_path(node.attrib['src'])
        full_url = urljoin(base_url, href)
        result.append(full_url)
    for child in node:
        result.extend(get_links_from_node(child, base_url))
    return result

def check_mimetype(filename, headers):
    f_type, f_encode = guess_type(str(filename))
    if not f_type:
        f_type = 'application/octet-stream'
    headers = Headers(headers)
    cont_type, cont_encode = parse_options_header(headers.get('Content-Type'))
    if f_type.lower() != cont_type.lower():
        raise ValueError(
            f"Content-type '{cont_type}' is different from filetype '{f_type}'"
            + f" guessed from '{filename}'"
        )


def get_links_from_css(css_file, base_url):
    """Get all links from a CSS file."""
    result = []
    text = css_file.read()
    parsed = cssutils.parseString(text)
    all_urls = cssutils.getUrls(parsed)
    for url in all_urls:
        result.append(urljoin(base_url, url))
    return result