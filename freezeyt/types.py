import os
import sys
from typing import Mapping, Any, Union, TYPE_CHECKING, Tuple, Callable
from typing import List, Literal, TypedDict, Optional, BinaryIO, Dict, Iterable
from typing import Coroutine
from types import TracebackType

from . import asgiref_typing
from freezeyt.compat import WSGIApplication

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

asgi_types = asgiref_typing

if TYPE_CHECKING:
    from .dictsaver import DictSaverContents
    from . import hooks

GetMimetypeFunction = Callable[[str], Optional[List[str]]]

SaverResult = Union[None, 'DictSaverContents']

ExceptionInfo = Tuple['type[BaseException]', BaseException, TracebackType]

WSGIExceptionInfo = Union[
    Tuple[None, None, None],
    ExceptionInfo,
    None,
]

WSGIHeaderList = List[Tuple[str, str]]

WSGIStartResponseResult = Callable[[bytes], object]

AnyApp = asgi_types.ASGI3Application | WSGIApplication

UrlFinder = Callable[
    [BinaryIO, str, Optional[WSGIHeaderList]],
    Union[Iterable[str], Coroutine[Any, Any, Iterable[str]]],
]

ActionFunction = Callable[['hooks.TaskInfo'], str]

class OutputConfig_dict(TypedDict):
    type: Literal['dict']

class OutputConfig_dir(TypedDict):
    type: Literal['dir']
    dir: str | os.PathLike[str]

class HooksConfig(TypedDict):
    start: NotRequired[List[str | Callable[['hooks.FreezeInfo'], object]]]
    page_frozen: NotRequired[List[str | Callable[['hooks.TaskInfo'], object]]]
    page_failed: NotRequired[List[str | Callable[['hooks.TaskInfo'], object]]]
    success: NotRequired[List[str | Callable[['hooks.FreezeInfo'], object]]]

class ExtraPagesConfig_generator(TypedDict):
    generator: str | Callable[[AnyApp], Iterable[str]]

ExtraPagesConfig = List[str | ExtraPagesConfig_generator]

class Config(TypedDict):
    version: NotRequired[int | str]
    default_mimetype: NotRequired[str]
    mime_db_file: NotRequired[str | os.PathLike[str]]
    get_mimetype: NotRequired[str | GetMimetypeFunction]
    static_mode: NotRequired[bool]
    app: NotRequired[str | AnyApp]
    fail_fast: NotRequired[bool]
    plugins: NotRequired[List[str | Callable[['hooks.FreezeInfo'], object]]]
    use_default_url_finders: NotRequired[bool]
    url_finders: NotRequired[Dict[str, str | UrlFinder]]
    status_handlers: NotRequired[Dict[str, str | ActionFunction]]
    output: str | os.PathLike[str] | OutputConfig_dict | OutputConfig_dir
    hooks: NotRequired[HooksConfig]
    cleanup: NotRequired[bool]
    prefix: NotRequired[str]
    extra_pages: NotRequired[List[str]]
    gh_pages: NotRequired[bool]
