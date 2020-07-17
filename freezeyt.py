import html5lib

def freeze(app, path):
    environ = {
        'SERVER_NAME': 'localhost',
        'wsgi.url_scheme': 'http',
        'SERVER_PORT': '8000',
        'REQUEST_METHOD': 'GET',
        # ...
    }

    def start_response(status, headers):
        print('status', status)
        print('headers', headers)

    result = app(environ, start_response)

    with open(path / "index.html", "wb") as f:
        for item in result:
            f.write(item)

    with open(path / "index.html", "rb") as f:
        links = get_all_links(f)

    for link in links:
        environ = {
            'SERVER_NAME': 'localhost',
            'wsgi.url_scheme': 'http',
            'SERVER_PORT': '8000',
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': link,
            # ...
        }

        result = app(environ, start_response)

        with open(path / link.lstrip('/'), "wb") as f:
            for item in result:
                f.write(item)
            
        with open(path / link.lstrip('/'), "rb") as f:
            links.extend(get_all_links(f))


def get_all_links(page_content):
    """Get all links from "page_content"

    Returns an iterable of strings
    """
    document = html5lib.parse(page_content)
    return get_links_from_node(document)


def get_links_from_node(node):
    """Get all links from xml.dom.minidom Node
    """
    result = []
    if 'href' in node.attrib:
        result.append(node.attrib['href'])
    for child in node:
        result.extend(get_links_from_node(child))
    return result

