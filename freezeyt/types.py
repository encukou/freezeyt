from typing import Mapping, Any, Union, TYPE_CHECKING, Tuple, Callable, Awaitable
from typing import List, NotRequired, TypedDict, Literal, Iterable
from types import TracebackType

from . import compat_asgiref_typing as asgi_types

if TYPE_CHECKING:
    from .dictsaver import DictSaverContents


Config = Mapping[str, Any]

SaverResult = Union[None, 'DictSaverContents']

ExceptionInfo = Tuple['type[BaseException]', BaseException, TracebackType]

WSGIExceptionInfo = Union[
    Tuple[None, None, None],
    ExceptionInfo,
    None,
]

WSGIHeaderList = List[Tuple[str, str]]

WSGIStartResponseResult = Callable[[bytes], object]
