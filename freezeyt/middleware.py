from typing import Iterable, Callable
import io
import pickle
import base64

from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, Forbidden, MethodNotAllowed
from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.security import safe_join
from werkzeug.utils import send_file

from a2wsgi.asgi_typing import ASGIApp, Scope, Receive, Send

from freezeyt.compat import StartResponse, WSGIEnvironment, WSGIApplication
from freezeyt.mimetype_check import MimetypeChecker
from freezeyt.extra_files import get_extra_files
from freezeyt.types import Config, WSGIHeaderList, WSGIExceptionInfo
from freezeyt.util import WrongMimetypeError


class ASGIMiddleware:
    def __init__(self, app: ASGIApp, config: Config):
        self.app = app
        self.static_mode = config.get('static_mode', False)

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
        await self.app(scope, receive, send)

    async def handle_non_get(
        self, scope: Scope, receive: Receive, send: Send,
    ) -> None:
        # Handle requests other than GET. These can't come from Freezeyt.
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
            await send({
                'type': "http.response.start",
                'status': 200, # OK
                'headers': [
                    (b'Allow', b'GET, HEAD, OPTIONS'),
                ],
            })
            await send({'type': "http.response.body"})
            return
        else:
            # Disallow other methods
            await send({
                'type': "http.response.start",
                'status': 405, # Method Not Allowed
                'headers': [],
            })
            await send({'type': "http.response.body"})
            return


class Middleware:
    def __init__(self, app: WSGIApplication, config: Config):
        self.app = app
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

        self.static_mode = config.get('static_mode', False)

    def __call__(
        self,
        environ: WSGIEnvironment,
        server_start_response: StartResponse,
    ) -> Iterable[bytes]:

        if self.static_mode:
            # Construct a new environment, only keeping the info that a server
            # of static pages would use
            COPIED_KEYS = {
                'REQUEST_METHOD',
                'SCRIPT_NAME',
                'PATH_INFO',
                # QUERY_STRING (URL parameters) is missing
                # CONTENT_TYPE & CONTENT_LENGTH (request body) is missing
                'SERVER_NAME',
                'SERVER_PORT',
                'SERVER_PROTOCOL',
                'HTTP_HOST',
                'wsgi.version',
                'wsgi.url_scheme',
                'wsgi.errors',
                'wsgi.multithread',
                'wsgi.multiprocess',
                'wsgi.run_once',
                'freezeyt.freezing',
            }
            new_environ = {
                **{
                    key: environ[key] for key
                    in COPIED_KEYS.intersection(environ)
                },
                'wsgi.input': io.BytesIO(b''),  # discard the request body
            }
            environ = new_environ

        path_info = environ.get('PATH_INFO', '')

        map_adapter = self.url_map.bind_to_environ(environ)
        try:
            endpoint, args = map_adapter.match()
        except NotFound:
            endpoint = 'app'
            args = {}
        except RequestRedirect as redirect:
            return redirect(environ, server_start_response)

        response: WSGIApplication
        if endpoint == 'content':
            response = Response(
                args['content'],
                mimetype=self.mimetype_checker.guess_mimetype(path_info),
            )
            return response(environ, server_start_response)
        if endpoint == 'path':
            base_path = args['path']
            extra_path = args['subpath']
            if extra_path:
                file_path = safe_join(str(base_path), str(extra_path))
                if file_path is None:
                    response = Forbidden()
                    return response(environ, server_start_response)
            else:
                file_path = base_path
            try:
                assert file_path is not None
                response = send_file(
                    file_path,
                    environ,
                    mimetype=self.mimetype_checker.guess_mimetype(path_info),
                )
            except FileNotFoundError:
                response = NotFound()
            except OSError:
                # This could have several different behaviors,
                # see https://github.com/encukou/freezeyt/issues/331
                # For now, return a 404
                response = NotFound()
            return response(environ, server_start_response)

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
