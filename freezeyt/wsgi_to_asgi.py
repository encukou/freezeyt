import io
import sys
import asyncio
import itertools

import freezeyt
from freezeyt.encoding import encode_wsgi_path, decode_input_path
from freezeyt.urls import PrefixURL


class WSGIToASGIMiddleware:
    def __init__(self, wsgi_app, *, prefix: PrefixURL):
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
            'wsgi.url_scheme': scope.get('scheme', 'http'),
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

        # The WSGI application can output data in two ways:
        # - by a "write" function, which, in our case, will append
        #   any data to a list, `wsgi_write_data`
        # - (preferably) by returning an iterable object.

        # See: https://www.python.org/dev/peps/pep-3333/#the-write-callable

        # The server should send body parts to the client *immediately*
        # after the "write" function is called.
        # We instead collect them and send them all at once, since we know
        # that the client (Freezeyt) won't mind.

        wsgi_write_data: List[bytes] = []

        def start_response(status, headers, exc_info):
            """WSGI start_response hook

            The application we are freezing will call this method
            and supply the status, headers, exc_info arguments.
            (self and wsgi_write are provided by freezeyt.)

            See: https://www.python.org/dev/peps/pep-3333/#the-start-response-callable

            Arguments:
                status: HTTP status line, like '200 OK'
                headers: HTTP headers (list of tuples)
                exc_info: Information about a server error, if any.
                    Will be raised if given.
            """
            if exc_info:
                exc_type, value, traceback = exc_info
                if value is not None:
                    raise value

            event = {
                'type': "http.response.start",
                'headers': [
                    (key.encode('latin-1'), value.encode('latin-1'))
                    for key, value in headers
                ],
                'status': int(status.split(maxsplit=1)[0]),
            }

            asyncio.create_task(send(event))

            return wsgi_write_data.append

        # Call the application. All calls to write (wsgi_write_data.append)
        # must be done as part of this call.
        result_iterable = self.wsgi_app(environ, start_response)

        try:
            for body_part in itertools.chain(wsgi_write_data, result_iterable):
                event = {
                    'type': "http.response.body",
                    'body': body_part,
                    'more_body': True,
                }
                await send(event)
            event = {
                'type': "http.response.body",
                'more_body': False,
            }
            await send(event)
        finally:
            close = getattr(result_iterable, 'close', None)
            if close is not None:
                close()
