from typing import Iterable

from werkzeug.wrappers import Response

from freezeyt.compat import StartResponse, WSGIEnvironment, WSGIApplication
from freezeyt.mimetype_check import MimetypeChecker
from freezeyt.extra_files import get_extra_files


class Middleware:
    def __init__(self, app: WSGIApplication, config):
        self.app = app
        self.mimetype_checker = MimetypeChecker(config)
        self.extra_file_contents = {}
        self.extra_file_paths = {}
        for url_part, kind, content_or_path in get_extra_files(config):
            if kind == 'content':
                self.extra_file_contents[url_part] = content_or_path
            elif kind == 'path':
                self.extra_file_paths[url_part] = content_or_path
            else:
                raise ValueError(kind)

    def __call__(
        self,
        environ: WSGIEnvironment,
        server_start_response: StartResponse,
    ) -> Iterable[bytes]:

        path_info = environ.get('PATH_INFO', '')

        stripped_path_info = path_info.lstrip('/')
        if stripped_path_info in self.extra_file_contents:
            response = Response(
                self.extra_file_contents[stripped_path_info],
                mimetype=self.mimetype_checker.guess_mimetype(path_info),
            )
            return response(environ, server_start_response)

        # XXX: This is a temporary hack
        for extra_file_url_part, path in self.extra_file_paths.items():
            if stripped_path_info.startswith(extra_file_url_part):
                extra_path = stripped_path_info[len(extra_file_url_part):]
                content = path.joinpath(extra_path.lstrip('/')).read_bytes()
                response = Response(
                    content,
                    mimetype=self.mimetype_checker.guess_mimetype(path_info),
                )
                return response(environ, server_start_response)

        def mw_start_response(status, headers, exc_info=None):
            result = server_start_response(status, headers, exc_info)
            self.mimetype_checker.check(path_info, headers)
            return result

        return self.app(environ, mw_start_response)
