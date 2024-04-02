from typing import Iterable, Callable
import pickle
import base64
from pathlib import PurePosixPath

from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.security import safe_join

from a2wsgi.asgi_typing import ASGIApp, Scope, Receive, Send

import freezeyt
from freezeyt.compat import StartResponse, WSGIEnvironment, WSGIApplication
from freezeyt.mimetype_check import MimetypeChecker
from freezeyt.extra_files import get_extra_files
from freezeyt.types import Config, WSGIHeaderList, WSGIExceptionInfo
from freezeyt.util import WrongMimetypeError


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
        assert scope['method'].isupper()
        if scope['method'] != 'GET':
            # The Freezer only sends GET requests.
            # When we get another method, we know it came from another WSGI
            # server. Handle it specially.
            await self.handle_non_get(scope, receive, send)
            return

        if self.static_mode:
            # Get the value of the 'host' header
            host = ''
            for name, value in scope['headers']:
                if name == b'host':
                    host = value
                    break

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
            new_scope = {
                **{
                    key: scope[key] for key
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
        headers = dict(scope['headers'])
        map_adapter = self.url_map.bind(
            server_name=headers[b'host'].decode('ascii'),
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
            await self.send_response(
                send,
                status=308,  # Permanent Redirect
                headers=[
                    (b'location', redirect.new_url.encode('ascii')),
                ],
                # TODO: a nice body
            )
            return

        if endpoint == 'content':
            mimetype = self.mimetype_checker.guess_mimetype(path_info)
            # TODO: does this need a charset?
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
                        headers=[],
                        # TODO: a nice body
                    )
                    return
            else:
                file_path = base_path
            try:
                assert file_path is not None
                # TODO: use a faster way to send the file
                with open(file_path, 'rb') as f:
                    content = f.read()
                mimetype=self.mimetype_checker.guess_mimetype(path_info)
                await self.send_response(
                    send,
                    status=200,  # OK
                    headers=[
                        (b'content-type', mimetype.encode('ascii')),
                    ],
                    body=content,
                )
                return
            except FileNotFoundError:
                await self.send_response(
                    send,
                    status=404,  # Not Found
                    headers=[],
                    # TODO: a nice body
                )
                return
            except OSError:
                # This could have several different behaviors,
                # see https://github.com/encukou/freezeyt/issues/331
                # For now, return a 404
                await self.send_response(
                    send,
                    status=404,  # Not Found
                    headers=[],
                    # TODO: a nice body
                )
                return

        await self.app(scope, receive, send)

    async def handle_non_get(
        self, scope: Scope, receive: Receive, send: Send,
    ) -> None:
        # Handle requests other than GET. These can't come from Freezeyt.

        # TODO: remove this header when WSGI middleware is gone
        scope = {
            **scope,
            'headers': [
                *scope['headers'],
                (b'freezeyt_skip_middleware', b'true'),
            ]
        }

        if not self.static_mode:
            # Normally, pass all other requests to the app unchanged.
            await self.app(scope, receive, send)
            return

        # In static mode, disallow everything but GET, HEAD, OPTIONS.

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

            # TODO: Should we call the middleware instead of the app?
            await self.app(scope, receive, head_send)
            return

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


class Middleware:
    def __init__(self, app: WSGIApplication, config: Config):
        self.app = app
        self.mimetype_checker = MimetypeChecker(config)

    def __call__(
        self,
        environ: WSGIEnvironment,
        server_start_response: StartResponse,
    ) -> Iterable[bytes]:

        # If the ASGI middleware tells us to skip processing, do so
        if 'HTTP_FREEZEYT_SKIP_MIDDLEWARE' in environ:
            return self.app(environ, server_start_response)

        path_info = environ.get('PATH_INFO', '')

        def mw_start_response(
            status: str,
            headers: WSGIHeaderList,
            exc_info: WSGIExceptionInfo = None,
        ) -> Callable[[bytes], object]:


            # HACK: Before we switch the middleware to ASGI, we need to
            # ensure the status handler error (like `UnexpectedStatus`
            # or `IgnorePage`) is raised before any error from the mimetype
            # check.
            # For now, we encode the exception with pickle+base64 to fit it
            # in a HTML header, and give it to the freezer to raise after
            # handling the status.
            # This is insecure (the freezer calls pickle on data from the
            # application). Don't merge! Switch to ASGI middleware first,
            # and remove the hack!
            error = None
            try:
                self.mimetype_checker.check(path_info, headers)
            except WrongMimetypeError as exc:
                is_freezing = (
                    'asgi.scope' in environ
                    and 'freezeyt.freezing' in environ['asgi.scope']
                )
                if is_freezing:
                    pickled_error = pickle.dumps(exc)
                    encoded_error = base64.b64encode(pickled_error)
                    headers = headers + [('Freezeyt-Error',
                                          encoded_error.decode('ascii'))]
                else:
                    error = exc
            result = server_start_response(status, headers, exc_info)
            if error:
                raise error

            return result

        return self.app(environ, mw_start_response)
