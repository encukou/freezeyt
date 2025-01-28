from typing import Mapping, Any, Union, TYPE_CHECKING, Tuple, Iterable
from typing import List, TypedDict
from types import TracebackType

import a2wsgi.asgi_typing

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
ASGIHeaders = Iterable[Tuple[bytes, bytes]]


# Freezeyt's HTTPScope has one extra key compared to ASGI HTTP scope:
# 'freezeyt.freezing'. Unfortunately:
# - ASGI says custom keys should have a dot
# - TypedDict can only inherit using the `class` syntax
# - `TypedDict`'s class syntax doesn't support keys with dots in them.
# So, we create `_FreezeytScopeExtra` using the non-class syntax, and
# inherit from it.

_FreezeytScopeExtra = TypedDict(
    '_FreezeytScopeExtra',
    {'freezeyt.freezing': bool},
)

class FreezeytHTTPScope(a2wsgi.asgi_typing.HTTPScope, _FreezeytScopeExtra):
    pass
