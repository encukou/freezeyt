from typing import Iterable

from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, Forbidden
from werkzeug.routing import Map, Rule
from werkzeug.routing.exceptions import RequestRedirect
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
                print("--MIDDLEWARE--")
                print(f"{self.url_map=}")
            else:
                raise ValueError(kind)

    def __call__(
        self,
        environ: WSGIEnvironment,
        server_start_response: StartResponse,
    ) -> Iterable[bytes]:

        path_info = environ.get('PATH_INFO', '')

        map_adapter = self.url_map.bind_to_environ(environ)
        try:
            endpoint, args = map_adapter.match()
            print(f"{(endpoint, args)=}")
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
                print(f"{file_path=}")
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
