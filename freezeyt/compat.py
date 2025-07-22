"""Utilities for compatibility with older versions of Python
"""

import sys
import asyncio
import shutil
import warnings
from typing import TypeVar, Literal

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


if sys.version_info >= (3, 12):
    rmtree = shutil.rmtree
else:
    def rmtree(path, ignore_errors=False, onexc=None):
        if onexc is None:
            onerror = None
        else:
            def onerror(function, path, exc_info):
                return onexc(function, path, exc_info[1])
        return shutil.rmtree(
            path,
            ignore_errors=ignore_errors,
            onerror=onerror,
        )

# In Python 3.11, freezeyt's MultiError derives from ExceptionGroup
# and can be used with the `except*` statement.
# In older versions, it derives from Exception instead.
if sys.version_info >= (3, 11):
    _MultiErrorBase = ExceptionGroup
    HAVE_EXCEPTION_GROUP: Literal[True] = True
else:
    _MultiErrorBase = Exception
    HAVE_EXCEPTION_GROUP: 'Literal[False]' = False

if sys.version_info >= (3, 12):
    warnings_warn = warnings.warn
else:
    # The skip_file_prefixes argument is new in Python 3.12.
    # Ignore it on earlier versions.
    def warnings_warn(*args, skip_file_prefixes=None, **kwargs):
        return warnings.warn(*args, **kwargs)

if sys.version_info >= (3, 11):
    asyncio_Barrier = asyncio.Barrier
else:
    class asyncio_Barrier:
        """Simple version of Barrier.

        Only handles one batch of parties.
        """
        def __init__(self, n):
            self.remaining = n
            self.event = None

        async def wait(self):
            if self.event is None:
                self.event = asyncio.Event()
            self.remaining -= 1
            if self.remaining <= 0:
                self.event.set()
            else:
                await self.event.wait()
