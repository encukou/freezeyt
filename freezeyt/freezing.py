from urllib.parse import urlparse, urljoin
from pathlib import Path
import xml.dom.minidom
import sys
import html5lib


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

    return base / url_path.lstrip('/')


def freeze(app, path, prefix='http://localhost:8000/'):
    """Freeze (create files of) all pages from a WSGI server.

    Parameters:
    app -- web app you want to freeze
    path -- path to the file
    prefix (url) -- URL to deploy web app
    """
    path = Path(path)

    prefix_parsed = parse_absolute_url(prefix)
    hostname = prefix_parsed.hostname
    port = prefix_parsed.port
    script_name = prefix_parsed.path

    def start_response(status, headers):
        if not status.startswith("200"):
            raise ValueError(f"Found broken link.")
        else:
            print('status', status)
            print('headers', headers)

    new_urls = [prefix]

    visited_urls = set()

    while new_urls:
        url = new_urls.pop()

        # url = http://freezeyt.test:1234/foo/

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
            'PATH_INFO': path_info,
            'SCRIPT_NAME': script_name,
            'SERVER_PROTOCOL': 'HTTP/1.1',

            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,

            'freezeyt.freezing': True,
        }

        result = app(environ, start_response)

        print(f'Saving to {filename}')

        filename.parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "wb") as f:
            for item in result:
                f.write(item)

        with open(filename, "rb") as f:
            new_urls.extend(get_all_links(f, url))


def get_all_links(page_content: bytes, base_url) -> list:
    """Get all links from "page_content".

    Return an iterable of strings.

    base_url is the URL of the page.
    """
    document = html5lib.parse(page_content)
    return get_links_from_node(document, base_url)


def get_links_from_node(node: xml.dom.minidom.Node, base_url) -> list:
    """Get all links from xml.dom.minidom Node."""
    result = []
    if 'href' in node.attrib:
        href = node.attrib['href']
        full_url = urljoin(base_url, href)
        result.append(full_url)
    if 'src' in node.attrib:
        href = node.attrib['src']
        full_url = urljoin(base_url, href)
        result.append(full_url)
    for child in node:
        result.extend(get_links_from_node(child, base_url))
    return result
