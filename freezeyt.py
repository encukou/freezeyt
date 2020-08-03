from urllib.parse import urlparse

import xml.dom.minidom

import html5lib

def url_to_filename(base, url):
    """Return the filename to which the page is frozen.

    Parameters:
    base - Filesystem base path (eg. /tmp/)
    url - Absolute or relative URL (eg. http://localhost:8000/ or /second/second.html)
    """
    url_parse = urlparse(url)

    if 'http' in url_parse.scheme:
        if url_parse.netloc == 'localhost:8000':
            url = url_parse.path
        else:
            raise ValueError("got external URL instead of localhost")
        if url == "":
            url = url + 'index.html'
        else:
            url = url_parse.path
    if url.endswith('/'):
        url = url + 'index.html'
    return base / url.lstrip('/')
    
def freeze(app, path):
    """Freeze (create files of) all pages from a WSGI server.

    Parameters:
    app -- web app you want to freeze
    path -- path to the file
    """
    def start_response(status, headers):
        print('status', status)
        print('headers', headers)

    links = ['/']

    visited_links = set()

    while links:
        link = links.pop()

        if link in visited_links:
            continue

        visited_links.add(link)

        print(link)

        environ = {
            'SERVER_NAME': 'localhost',
            'wsgi.url_scheme': 'http',
            'SERVER_PORT': '8000',
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': link,
            # ...
        }

        result = app(environ, start_response)

        with open(url_to_filename(path, link), "wb") as f:
            for item in result:
                f.write(item)

        with open(url_to_filename(path, link), "rb") as f:
            links.extend(get_all_links(f))


def get_all_links(page_content: bytes) -> list:
    """Get all links from "page_content".

    Return an iterable of strings.
    """
    document = html5lib.parse(page_content)
    return get_links_from_node(document)


def get_links_from_node(node: xml.dom.minidom.Node) -> list:
    """Get all links from xml.dom.minidom Node."""
    result = []
    if 'href' in node.attrib:
        result.append(node.attrib['href'])
    for child in node:
        result.extend(get_links_from_node(child))
    return result
