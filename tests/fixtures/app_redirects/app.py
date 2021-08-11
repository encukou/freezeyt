from wsgiref.simple_server import make_server
from urllib.parse import quote

REDIRECT_CODES = 301, 308, 302, 303, 307, 300, 304

def generate_urls(app):
    for code in REDIRECT_CODES:
        yield f'absolute/{code}/'
        yield f'relative/{code}/'
        yield f'no_port/{code}/'

freeze_config = {
    'prefix': 'http://example.test/',
    'extra_pages': [{'generator': 'app:generate_urls'}],
    'redirect_policy': 'save',
}

# Flask always rewrites "Location:" headers to be absolute
# URLs, so we use a raw WSGI application to test redirect
# behavior.
# The app has these URLs:
# / : returns 200 response with "All OK" in the body
# /absolute/<code> : redirects to / with the given HTTP code
#                    using an absolute URL for /
# /relative/<code> : redirects to / with the given HTTP code
#                    using a relative URL for /


def app(environ, start_response):
    path = environ['PATH_INFO']
    if path == '/':
        start_response('200 OK', [
            ('Content-Type', 'text/html'),
        ])
        return [b'All OK']

    def respond_404():
        start_response('404 Not Found', [])
        return [b'Not found']

    try:
        # path is e.g. '/relative/300/'
        empty1, redirect_type, code, empty2 = path.split('/')
    except ValueError:
        # more or less than 4 parts
        return respond_404()
    if empty1 != '' or empty2 != '':
        return respond_404()
    if redirect_type == 'absolute':

        # URL reconstruction from
        # https://www.python.org/dev/peps/pep-3333/#url-reconstruction
        url = environ['wsgi.url_scheme']+'://'
        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']
            url += ':' + environ['SERVER_PORT']
        url += quote(environ.get('SCRIPT_NAME', ''))

    elif redirect_type == 'relative':
        url = (
            quote(environ.get('SCRIPT_NAME', '/'))
        )
        assert url.startswith('/')
    elif redirect_type == 'no_port':
        # Redirest to "prefix" without the port number
        url = 'http://example.test/'
    else:
        return respond_404()
    try:
        code = int(code)
    except ValueError:
        return respond_404()
    start_response(
        f'{code} SOME REDIRECT',
        [
            ('Location', url),
            ('Content-Type', 'text/html'),
        ]
    )
    return [b'Redirecting...']


if __name__ == '__main__':
    with make_server('', 5000, app) as httpd:
        print("Serving HTTP on port 5000...")
        httpd.serve_forever()


expected_dict = {
    'index.html': b"All OK",
    "absolute": {
        str(code): {"index.html": b'Redirecting...'} for code in REDIRECT_CODES
    },
    "relative": {
        str(code): {"index.html": b'Redirecting...'} for code in REDIRECT_CODES
    },
    "no_port": {
        str(code): {"index.html": b'Redirecting...'} for code in REDIRECT_CODES
    },
}


expected_dict_follow = {
    'index.html': b"All OK",
    "absolute": {
        str(code): {"index.html": b'All OK'} for code in REDIRECT_CODES
    },
    "relative": {
        str(code): {"index.html": b'All OK'} for code in REDIRECT_CODES
    },
    "no_port": {
        str(code): {"index.html": b'All OK'} for code in REDIRECT_CODES
    },
}


expected_dict_ignore = {
    'index.html': b"All OK",
}
