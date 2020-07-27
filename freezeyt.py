import html5lib


def url_to_filename(base, url):
    """Return the filename to which the page is frozen.

    base -- path to the file
    url -- web app endpoint of the page
    """
    if url.endswith('/'):
        url = url + 'index.html'
    return base / url.lstrip('/')


def freeze(app, path):
    """Freeze (create files of) all pages from a WSGI server.

    Arguments:
    app -- web app you want to freeze
    path -- path to the file
    """
    def start_response(status, headers):
        print('status', status)
        print('headers', headers)

    links = set('/')

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
            links = links.union(set(get_all_links(f)))


def get_all_links(page_content):
    """Get all links from "page_content".

    Return an iterable of strings.
    """
    document = html5lib.parse(page_content)
    return get_links_from_node(document)


def get_links_from_node(node):
    """Get all links from xml.dom.minidom Node."""
    result = set()
    if 'href' in node.attrib:
        result.add(node.attrib['href'])
    for child in node:
        result = result.union(get_links_from_node(child))
    return result
