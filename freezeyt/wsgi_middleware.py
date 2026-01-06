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


class WSGIMiddleware:
    def __init__(self, app: WSGIApplication, config: Config):
        self.app = app
        self.mimetype_checker = MimetypeChecker(config)

    def __call__(
        self,
        environ: WSGIEnvironment,
        server_start_response: StartResponse,
    ) -> Iterable[bytes]:

        path_info = environ.get('PATH_INFO', '')

        def mw_start_response(
            status: str,
            headers: WSGIHeaderList,
            exc_info: WSGIExceptionInfo = None,
        ) -> Callable[[bytes], object]:
            result = server_start_response(status, headers, exc_info)
            try:
                self.mimetype_checker.check(path_info, headers)
            except Exception as e:
                if task := environ.get('freezeyt.task'):
                    print(task)
                    task.error = e
                else:
                    raise
            return result

        return self.app(environ, mw_start_response)
