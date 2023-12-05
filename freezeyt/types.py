from typing import NewType, Mapping, Any, Union, Dict, TYPE_CHECKING
import urllib.parse

if TYPE_CHECKING:
    from .dictsaver import DictSaverContents


Config = Mapping[str, Any]

SaverResult = Union[None, 'DictSaverContents']

# An URL as used internally by Freezeyt.
# Absolute IRI, with an explicit port if it's `http` or `https`
AbsoluteURL = NewType('AbsoluteURL', urllib.parse.SplitResult)
