from typing import NewType, Mapping, Any, Union
import urllib.parse

Config = Mapping[str, Any]

SaverResult = Union[None, dict]

# An URL as used internally by Freezeyt.
# Absolute IRI, with an explicit port if it's `http` or `https`
AbsoluteURL = NewType('AbsoluteURL', urllib.parse.SplitResult)
