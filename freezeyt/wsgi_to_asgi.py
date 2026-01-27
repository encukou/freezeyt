import io
import sys
import itertools
from typing import List, Dict

import freezeyt
from freezeyt.encoding import encode_wsgi_path
from freezeyt.urls import PrefixURL
from freezeyt.types import WSGIExceptionInfo


class WSGIToASGIMiddleware:
    """Middleware that converts a WSGI app into an ASGI app."""

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

        scheme = scope.get('scheme', 'http')
        DEFAULT_PORTS = {'http': 80, 'https': 443}

        environ: Dict[str, object] = {
            'HTTP_HOST': self.prefix.hostname,  # default; overridden below
            'SERVER_NAME': self.prefix.hostname,  # default; overridden below
            'SERVER_PORT': str(self.prefix.port), # default; overridden below
            'REQUEST_METHOD': scope['method'],
            'PATH_INFO': encode_wsgi_path(path_info),
            'SCRIPT_NAME': encode_wsgi_path(prefix_path),
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'SERVER_SOFTWARE': f'freezeyt/{freezeyt.__version__}',

            'wsgi.version': (1, 0),
            'wsgi.url_scheme': scheme,
            'wsgi.input': io.BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,

            'freezeyt.freezing': scope.get('freezeyt.freezing', False),
            'freezeyt.task': scope.get('freezeyt.task', None),
        }
        if 'raw_path' in scope:
            environ['RAW_URI'] = scope['raw_path']
        server = scope.get('server')
        if server:
            hostname, port = server
            environ['SERVER_NAME'] = hostname
            if port is None:
                port = DEFAULT_PORTS[scheme]
            if port == DEFAULT_PORTS[scheme]:
                environ['HTTP_HOST'] = hostname
            else:
                environ['HTTP_HOST'] = hostname + ':' + str(port)
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
        start_event = None

        def start_response(status, headers, exc_info: WSGIExceptionInfo = None):
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
            nonlocal start_event

            if exc_info:
                exc_type, value, traceback = exc_info
                if value is not None:
                    raise value

            if start_event:
                raise AssertionError(
                    'WSGI application called start_response twice')

            start_event = {
                'type': "http.response.start",
                'headers': [
                    (key.encode('latin-1'), value.encode('latin-1'))
                    for key, value in headers
                ],
                'status': int(status.split(maxsplit=1)[0]),
            }

            return wsgi_write_data.append

        # Call the application. All calls to write (wsgi_write_data.append)
        # must be done as part of this call.
        result_iterable = self.wsgi_app(environ, start_response)

        if not start_event:
            raise AssertionError(
                'WSGI application did not call start_response')
        await send(start_event)

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
