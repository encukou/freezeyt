# An invalid WSGI app that calls start_response twice


def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'You should not see this']


if __name__ == '__main__':
    # The WSGI server fails with:
    #    AssertionError: Headers already set!
    from wsgiref.simple_server import make_server
    with make_server('', 5000, app) as httpd:
        print("Serving HTTP on port 5000...")
        httpd.serve_forever()
