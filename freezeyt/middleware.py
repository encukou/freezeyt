from typing import Optional
from pathlib import PurePosixPath
import warnings
import os.path
import io

from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.security import safe_join

from a2wsgi import ASGIMiddleware as asgi_to_wsgi
from a2wsgi import WSGIMiddleware as wsgi_to_asgi

from a2wsgi.asgi_typing import ASGIApp, Scope, HTTPScope, Receive, Send

import freezeyt
from freezeyt.mimetype_check import MimetypeChecker
from freezeyt.extra_files import get_extra_files
from freezeyt.types import Config, ASGIHeaders


def get_path_info(root_path: str, request_path: str) -> str:
    """Given ASGI root_path and path, get the WSGI "script name"

    That is, strip root_path from the beginning of request_path
    """
    root = PurePosixPath('/') / root_path
    req = PurePosixPath('/') / request_path
    path_info = str(req.relative_to(root))
    if request_path.endswith('/'):
        path_info += '/'
    return path_info


def get_header_value(
    headers: ASGIHeaders, header_name: bytes,
) -> Optional[bytes]:
    """Get the value of the first header with the given name"""
    assert header_name.islower()
    for name, value in headers:
        if name.lower() == header_name:
            return value
    return None


class ASGIMiddleware:
    def __init__(self, app: ASGIApp, config: Config):
        self.app = app
        self.static_mode = config.get('static_mode', False)
        self.mimetype_checker = MimetypeChecker(config)
        self.url_map = Map()
        for url_part, kind, content_or_path in get_extra_files(config):
            if '<' in url_part:
                raise NotImplementedError("the extra file URL cannot include '<'")
            if kind == 'content':
                self.url_map.add(Rule(
                    f'/{url_part}',
                    endpoint='content',
                    defaults={'content': content_or_path},
                ))
            elif kind == 'path':
                self.url_map.add(Rule(
                    f'/{url_part}',
                    endpoint='path',
                    defaults={'path': content_or_path, 'subpath': None},
                ))
                self.url_map.add(Rule(
                    f'/{url_part}/<path:subpath>',
                    endpoint='path',
                    defaults={'path': content_or_path},
                ))
            else:
                raise ValueError(kind)

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        assert scope['method'].isupper()
        if scope['method'] != 'GET':
            # The Freezer only sends GET requests.
            # When we get another method, we know it came from another WSGI
            # server. Handle it specially.
            await self.handle_non_get(scope, receive, send)
            return

        # Get the value of the 'host' header
        host = get_header_value(scope['headers'], b'host') or b''

        if self.static_mode:
            # Construct a new scope, only keeping the info that a server
            # of static pages would use
            COPIED_KEYS = {
                'type',
                'asgi',
                'http_version',
                'method',
                'scheme',
                'path',
                'root_path',
                'server',
                'freezeyt.freezing',
            }
            new_scope: HTTPScope = {
                **{
                    # these keys are known strings that exist in the original
                    # `scope`, but mypy doesn't know that.
                    key: scope[key] for key  # type: ignore
                    in COPIED_KEYS.intersection(scope)
                },
                'query_string': b'',  # URL parameters are missing
                'headers': [
                    (b'host', host),
                    (b'user-agent', f'freezeyt/{freezeyt.__version__}'.encode()),
                    (b'freezeyt-freezing', b'True'),
                ],
            }
            scope = new_scope

        path_info = get_path_info(scope['root_path'], scope['path'])
        map_adapter = self.url_map.bind(
            server_name=host.decode('ascii'),
            script_name=scope['root_path'],
            url_scheme=scope['scheme'],
            default_method=scope['method'],
            path_info=path_info,
        )
        try:
            endpoint, args = map_adapter.match()
        except NotFound:
            endpoint = 'app'
            args = {}
        except RequestRedirect as redirect:
            # It might not be possible to get a RequestRedirect from the
            # werkzeug URL Map, the way we have it set up.
            # (If there is a way, it would be nice to send a nice body
            # in the redirecting response.)
            await self.send_response(
                send,
                status=308,  # Permanent Redirect
                headers=[
                    (b'location', redirect.new_url.encode('ascii')),
                ],
            )
            return

        if endpoint == 'content':
            mimetype = self.mimetype_checker.guess_mimetype(path_info)
            if mimetype.startswith('text/'):
                # Use a modern default for text files.
                mimetype += '; charset=utf-8'
            await self.send_response(
                send,
                headers=[
                    (b'content-type', mimetype.encode('ascii')),
                ],
                body=args['content'],
            )
            return
        if endpoint == 'path':
            base_path = args['path']
            extra_path = args['subpath']
            if extra_path:
                file_path = safe_join(str(base_path), str(extra_path))
                if file_path is None:
                    await self.send_response(
                        send,
                        status=403,  # Forbidden
                        headers=[
                            (b'content-type', b'text/plain; charset=ascii'),
                        ],
                        body=b'Forbidden.',
                    )
                    return
            else:
                file_path = base_path
            assert file_path is not None
            mimetype = self.mimetype_checker.guess_mimetype(path_info)
            if not os.path.isfile(file_path):
                await self.send_response(
                    send,
                    status=404,  # Not Found
                    headers=[
                        (b'content-type', b'text/plain; charset=ascii'),
                    ],
                    body=b'Not found.',
                )
                return
            await send({
                'type': "http.response.start",
                'status': 200,  # OK
                'headers': [
                    (b'content-type', mimetype.encode('ascii')),
                ],
            })
            if "http.response.pathsend" in scope.get('extensions', {}):
                await send({
                    'type': "http.response.pathsend",
                    'path': file_path,
                })
                return
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(io.DEFAULT_BUFFER_SIZE)
                    if chunk:
                        await send({
                            'type': "http.response.body",
                            'body': chunk,
                            'more_body': True,
                        })
                    else:
                        await send({
                            'type': "http.response.body",
                        })
                        return

        async def middleware_send(event):
            await send(event)
            if event['type'] == "http.response.start":
                content_type = get_header_value(
                    event['headers'], b'content-type',
                )
                wsgi_headers = [
                    ('Content-Type', (content_type or b'').decode('ascii')),
                ]
                self.mimetype_checker.check(path_info, wsgi_headers)

        await self.app(scope, receive, middleware_send)

    async def handle_non_get(
        self, scope: HTTPScope, receive: Receive, send: Send,
    ) -> None:
        # Handle requests other than GET. These can't come from Freezeyt.

        # HEAD should match GET: we should route it through the middleware
        # in order to handle static files.

        if scope['method'] == 'HEAD':
            # For HEAD, call the app but ignore the response body

            # ASGI wants us to copy scope before modifying it, see
            # https://asgi.readthedocs.io/en/latest/specs/main.html#middleware
            scope = {**scope, 'method': 'GET'}

            async def head_send(event):
                if event['type'] == "http.response.body":
                    pass
                elif event['type'] == "http.response.start":
                    await send(event)
                    # indicate the end of the (empty) body
                    await send({'type': "http.response.body"})
                # We're in static mode; we don't support other events.

            await self(scope, receive, head_send)
            return

        # Normally, pass all other requests to the app unchanged.

        if not self.static_mode:
            await self.app(scope, receive, send)
            return

        # In static mode, disallow everything but GET, HEAD, OPTIONS.

        elif scope['method'] == 'OPTIONS':
            # For OPTIONS, give our own response
            # (The status should be '204 No Content', but according to
            # MDN, some browsers misinterpret that, so '200' is safer.)
            await self.send_response(
                send,
                status=200, # OK
                headers=[
                    (b'Allow', b'GET, HEAD, OPTIONS'),
                ],
            )
            return
        else:
            # Disallow other methods
            await self.send_response(
                send,
                status=405, # Method Not Allowed
                headers=[],
            )
            return

    async def send_response(self, send, *, status=200, headers, body=b''):
        await send({
            'type': "http.response.start",
            'status': status,
            'headers': headers,
        })
        await send({'type': "http.response.body", 'body': body})


def Middleware(wsgi_app, config):
    warnings.warn(
        "freezeyt.Middleware is deprecated. Use ASGIMiddleware if you have an "
        "ASGI app; or WSGIMiddleware as a direct replacement.",
        DeprecationWarning,
    )
    return WSGIMiddleware(wsgi_app, config)

def WSGIMiddleware(wsgi_app, config):
    # Since our ASGI middleware handles everything, this turns WSGI to ASGI,
    # applies our middleware, and turns ASGI back to WSGI.
    # That's a lot of overhead. Use ASGI if you can.

    asgi_app = wsgi_to_asgi(wsgi_app)
    middlewared_asgi_app = ASGIMiddleware(asgi_app, config)
    return asgi_to_wsgi(middlewared_asgi_app)
