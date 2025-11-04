import freezeyt

class WSGIToASGIMiddleware:
    def __init__(self, wsgi_app, *, prefix):
        self.wsgi_app = wsgi_app
        self.prefix = prefix

    async def __call__(self, scope, receive, send):
        path_info = scope['path']

        prefix_path = scope.get('root_path', '')
        if not prefix_path.endswith('/'):
            prefix_path += '/'

        if path_info.startswith(prefix_path):
            path_info = "/" + path_info[len(prefix_path):]

        environ: WSGIEnvironment = {
            'SERVER_NAME': self.prefix.hostname,  # default; overridden below
            'SERVER_PORT': str(self.prefix.port), # default; overridden below
            'REQUEST_METHOD': scope['method'],
            'PATH_INFO': encode_wsgi_path(path_info),
            'SCRIPT_NAME': encode_wsgi_path(prefix_path),
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'SERVER_SOFTWARE': f'freezeyt/{freezeyt.__version__}',

            'wsgi.version': (1, 0),
            'wsgi.url_scheme': scope.get('scheme', 'http')
            'wsgi.input': io.BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,

            'freezeyt.freezing': scope.get('freezeyt.freezing', False),
        }
        server = scope.get('server')
        if server:
            hostname, port = server
            environ['SERVER_NAME'] = hostname
            if port is None:
                port = 80
            environ['SERVER_PORT'] = str(port)

        def start_response(status, headers, exc_info):
            ...

        result = self.wsgi_app(environ, start_response)

        await send(...)
