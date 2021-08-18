from wsgiref.simple_server import make_server
from urllib.parse import quote

REDIRECT_CODES = 301, 308, 302, 303, 307, 300, 304

def generate_urls(app):
    for code in REDIRECT_CODES:
        yield f'absolute/{code}/'
        yield f'no_host/{code}/'
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
# /no_host/<code> : redirects to / with the given HTTP code
#                    using a URL without a host
# /relative/<code> : redirects to / with the given HTTP code
#                    using the URL '../..'
# /no_port/<code> :  redirects to / with the given HTTP code
#                    using a absolute URL with no port number


def app(environ, start_response):
    path = environ['PATH_INFO']

    # Handle the "home page" to which everything redirects
    if path == '/':
        start_response('200 OK', [
            ('Content-Type', 'text/html'),
        ])
        return [b'All OK']

    # Helper for pages we don't handle
    def respond_404():
        start_response('404 Not Found', [])
        return [b'Not found']

    # Parse the request's path to get the redirect URL type and code
    # path is e.g. '/relative/300/'
    try:
        empty1, redirect_type, code, empty2 = path.split('/')
    except ValueError:
        # more or less than 4 parts
        return respond_404()
    if empty1 != '' or empty2 != '':
        return respond_404()

    # Get the URL to put in the Location header
    if redirect_type == 'absolute':
        url = reconstruct_url(environ)
    elif redirect_type == 'no_host':
        url = quote(environ.get('SCRIPT_NAME', '/'))
        if url == '':
            url = '/'
    elif redirect_type == 'relative':
        url = '../../'
    elif redirect_type == 'no_port':
        # Redirest to "prefix" without the port number
        url = reconstruct_url(environ, include_port=False)
    else:
        return respond_404()

    # Verify the status code
    try:
        code = int(code)
    except ValueError:
        return respond_404()
    if not (300 <= code <= 399):
        return respond_404()

    # Construct the response headers and body
    start_response(
        f'{code} SOME REDIRECT',
        [
            ('Location', url),
            ('Content-Type', 'text/html'),
        ]
    )
    return [b'Redirecting...']


def reconstruct_url(environ, include_port=True):
    # URL reconstruction from
    # https://www.python.org/dev/peps/pep-3333/#url-reconstruction
    # but we either always or never include the port number.
    url = environ['wsgi.url_scheme']+'://'
    url += environ['SERVER_NAME']
    if environ['wsgi.url_scheme'] == 'https':
        default_port = '443'
    else:
        default_port = '80'
    if include_port:
        url += ':' + environ['SERVER_PORT']
    else:
        if environ['SERVER_PORT'] != default_port:
            raise ValueError(
                'For no_port, the default port (80 or 443) must be used')
    url += quote(environ.get('SCRIPT_NAME', ''))
    return url


if __name__ == '__main__':
    with make_server('', 5000, app) as httpd:
        print("Serving HTTP on port 5000...")
        httpd.serve_forever()


expected_dict = {
    'index.html': b"All OK",
    "absolute": {
        str(code): {"index.html": b'Redirecting...'} for code in REDIRECT_CODES
    },
    "no_host": {
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
    "no_host": {
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
