import warnings

from freezeyt.actions import warn, follow, ignore, save, error
from freezeyt.actions import ActionFunction as StatusHandler

__all__ = [
    'warn', 'follow', 'ignore', 'save', 'error',
    'StatusHandler',
]

warnings.warn(
    'The status_handlers module is deprecated, use freezeyt.actions',
    DeprecationWarning,
)
