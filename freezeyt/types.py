from typing import Mapping, Any, Union, TYPE_CHECKING, Tuple, Callable
from typing import List
from types import TracebackType

from . import compat_asgiref_typing

asgi_types = compat_asgiref_typing

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
