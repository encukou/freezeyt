from typing import Iterable, Callable
import io

from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, Forbidden, MethodNotAllowed
from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.security import safe_join
from werkzeug.utils import send_file

from freezeyt.compat import StartResponse, WSGIEnvironment, WSGIApplication
from freezeyt.mimetype_check import MimetypeChecker
from freezeyt.extra_files import get_extra_files
from freezeyt.types import Config, WSGIHeaderList, WSGIExceptionInfo


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

        if environ['REQUEST_METHOD'] != 'GET':
            # The Freezer only sends GET requests.
            # When we get another method, we know it came from another WSGI
            # server. Handle it specially.
            return self.handle_non_get(environ, server_start_response)

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
            result = server_start_response(status, headers, exc_info)
            self.mimetype_checker.check(path_info, headers)
            return result

        return self.app(environ, mw_start_response)

    def handle_non_get(
        self, environ: WSGIEnvironment,
        server_start_response: StartResponse,
    ) -> Iterable[bytes]:
        # Handle requests other than GET. These can't come from Freezeyt.
        if not self.static_mode:
            # Normally, pass all other requests to the app unchanged.
            return self.app(environ, server_start_response)

        # In static mode, disallow everything but GET, HEAD, OPTIONS.

        if environ['REQUEST_METHOD'] == 'HEAD':
            # For HEAD, call the app but ignore the response body
            environ['REQUEST_METHOD'] = 'GET'
            body_iterator = self.app(environ, server_start_response)
            try:
                # self.app is typed as returning just an iterable of bytes,
                # but the WSGI spec says that if that iterable has a `close`
                # method, we need to call it.
                # Hence a type ignore.
                close = body_iterator.close  # type: ignore[attr-defined]
            except AttributeError:
                pass
            else:
                close()
            return []
        elif environ['REQUEST_METHOD'] == 'OPTIONS':
            # For OPTIONS, give our own response
            # (The status should be '204 No Content', but according to
            # MDN, some browsers misinterpret that, so '200' is safer.)
            server_start_response(
                '200 No Content',
                [('Allow', 'GET, HEAD, OPTIONS')],
            )
            return []
        else:
            # Disallow other methods
            response = MethodNotAllowed()
            return response(environ, server_start_response)
