"""Utilities for compatibility with older versions of Python
"""

import sys
import asyncio
from typing import TYPE_CHECKING, TypeVar, Coroutine, Any, Optional

if sys.version_info >= (3, 8) or TYPE_CHECKING:
    from typing import Literal

T = TypeVar('T')

if sys.version_info >= (3, 11):
    import wsgiref.types
    StartResponse = wsgiref.types.StartResponse
    WSGIEnvironment = wsgiref.types.WSGIEnvironment
    WSGIApplication = wsgiref.types.WSGIApplication
else:
    import typing
    StartResponse = typing.Callable
    WSGIEnvironment = dict
    WSGIApplication = typing.Any

if sys.version_info >= (3, 10):
    from typing import ParamSpec, Concatenate
else:
    from typing_extensions import ParamSpec, Concatenate


if sys.version_info >= (3, 7):
    asyncio_run = asyncio.run
else:
    def asyncio_run(awaitable):
        """asyncio.run for Python 3.6"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(awaitable)
        # We should also call loop.close() here, but that would mean
        # the event loop can't be used in other code:
        # * when using freezeyt as a library, and
        # * in our own tests.
        # So, we cheat a bit and don't call close().
        # (Python 3.6 support is ending soon, anyway.)


def asyncio_create_task(
    coroutine: 'Coroutine[Any, Any, T]',
    name: 'Optional[str]',
) -> 'asyncio.Task[T]':
    """asyncio.create_task for Python 3.6 & 3.7"""
    if sys.version_info < (3, 7):
        # Python 3.6
        return asyncio.ensure_future(coroutine)
    elif sys.version_info < (3, 8):
        # Python 3.7
        return asyncio.create_task(coroutine)
    else:
        return asyncio.create_task(coroutine, name=name)


def get_running_loop() -> asyncio.AbstractEventLoop:
    try:
        get_loop = asyncio.get_running_loop
    except AttributeError:
        # Python 3.6
        return asyncio.get_event_loop()
    else:
        return get_loop()


# In Python 3.11, freezeyt's MultiError derives from ExceptionGroup
# and can be used with the `except*` statement.
# In older versions, it derives from Exception instead.
if sys.version_info >= (3, 11):
    _MultiErrorBase = ExceptionGroup[Exception]
    HAVE_EXCEPTION_GROUP: Literal[True] = True
else:
    _MultiErrorBase = Exception
    HAVE_EXCEPTION_GROUP: 'Literal[False]' = False
