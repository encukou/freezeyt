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

    links = get_all_links(result)


def get_all_links(page_content):
    """Get all links from "page_content"

    Returns an iterable of strings
    """
    result = []
    print(page_content)
    document = html5lib.parse(page_content)
    print(document)
    for child in document:
        for grandchild in child:
            print(grandchild)
            print(grandchild.tag)
            if grandchild.tag == '{http://www.w3.org/1999/xhtml}a':
                print(grandchild.attrib)
                result.append(grandchild.attrib['href'])
    return result
