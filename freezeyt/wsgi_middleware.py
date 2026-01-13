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

    def __call__(
        self,
        environ: WSGIEnvironment,
        server_start_response: StartResponse,
    ) -> Iterable[bytes]:
        return self.app(environ, server_start_response)
