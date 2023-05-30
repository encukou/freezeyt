from typing import Iterable

from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, Forbidden, MethodNotAllowed
from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.security import safe_join
from werkzeug.utils import send_file

from freezeyt.compat import StartResponse, WSGIEnvironment, WSGIApplication
from freezeyt.mimetype_check import MimetypeChecker
from freezeyt.extra_files import get_extra_files


class Middleware:
    def __init__(self, app: WSGIApplication, config):
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
            new_environ = {
                'REQUEST_METHOD': environ['REQUEST_METHOD'],
                'SCRIPT_NAME': environ.get('SCRIPT_NAME', ''),
                'PATH_INFO': environ.get('PATH_INFO', ''),
                'SERVER_NAME': environ.get('SERVER_NAME', ''),
                'SERVER_PORT': environ.get('SERVER_PORT', ''),
                'SERVER_PROTOCOL': environ.get('SERVER_PROTOCOL', ''),
                'HTTP_HOST': environ.get('HTTP_HOST', ''),
                'wsgi.version': environ.get('wsgi.version', ''),
                'wsgi.url_scheme': environ.get('wsgi.url_scheme', ''),
                'wsgi.input': 'XXX_TODO',
                'wsgi.errors': environ.get('wsgi.errors', ''),
                'wsgi.multithread': environ.get('wsgi.multithread', ''),
                'wsgi.multiprocess': environ.get('wsgi.multiprocess', ''),
                'wsgi.run_once': environ.get('wsgi.run_once', ''),
                'freezeyt.freezing': environ.get('freezeyt.freezing', ''),
            }
            environ = new_environ

        if environ['REQUEST_METHOD'] != 'GET':
            # The Freezer only sends GET requests.
            # When we get another method, we know it came from another WSGI
            # server. Handle it specially.
            return self.handle_non_get(environ, server_start_response)

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

        def mw_start_response(status, headers, exc_info=None):
            result = server_start_response(status, headers, exc_info)
            self.mimetype_checker.check(path_info, headers)
            return result

        return self.app(environ, mw_start_response)

    def  handle_non_get(self, environ, server_start_response):
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
                close = body_iterator.close
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
                {'Allow': 'GET, HEAD, OPTIONS'},
            )
            return []
        else:
            # Disallow other methods
            response = MethodNotAllowed()
            return response(environ, server_start_response)
