from typing import NewType, Mapping, Any

Config = Mapping[str, Any]

# An URL as used internally by Freezeyt.
# Absolute IRI, with an explicit port if it's `http` or `https`
AbsoluteURL = typing.NewType('AbsoluteURL', urllib.parse.SplitResult)
