
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

    with open("/tmp/frozen/index.html", "wb") as f:
        for item in result:
            f.write(item)
