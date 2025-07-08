import urllib.parse
import functools
from typing import Union

from werkzeug.urls import uri_to_iri

from freezeyt.util import RelativeURLError, UnsupportedSchemeError
from freezeyt.util import BadPrefixError, ExternalURLError


def split_iri(url):
    return urllib.parse.urlsplit(uri_to_iri(url))


def get_port(port, scheme):
    if port:
        return port
    elif scheme == 'http':
        return 80
    else:
        return 443


class PrefixURL:
    """An URL as used internally by Freezeyt.

    Absolute `http` or `https` IRI, with an explicit port, ending with a slash.
    For example:
        https://localhost:80/some-path/
    """
    def __init__(self, str_or_splitresult: Union[str, urllib.parse.SplitResult], /):
        _url = str_or_splitresult
        split_url: urllib.parse.SplitResult
        if isinstance(str_or_splitresult, str):
            split_url = split_iri(str_or_splitresult)
        else:
            split_url = str_or_splitresult
        if not split_url.scheme:
            raise RelativeURLError(f"Expected an absolute URL, not {_url}")

        if split_url.scheme not in ('http', 'https'):
            raise UnsupportedSchemeError(f"URL scheme must be http or https: {_url}")

        if not split_url.netloc:
            raise RelativeURLError(f"Expected an absolute URL, not {_url}")

        if split_url.query:
            raise BadPrefixError("The prefix cannot have a query part")

        if split_url.fragment:
            raise BadPrefixError("The prefix cannot have a fragment part")

        if not split_url.path.endswith('/'):
            raise BadPrefixError("The prefix must end with a slash")

        self._split_url = split_url

    def __str__(self):
        return urllib.parse.urlunsplit(self._split_url)

    @property
    def scheme(self):
        return self._split_url.scheme

    @property
    def hostname(self):
        return self._split_url.hostname

    @property
    def port(self):
        return get_port(self._split_url.port, self._split_url.scheme)

    @property
    def netloc(self):
        return self._split_url.netloc

    @property
    def path(self):
        return self._split_url.path

    def _replace_path(self, path):
        return PrefixURL(self._split_url._replace(path=path))

    def as_app_url(self):
        return AppURL(self._split_url, self)

    def join(self, link_text: str) -> 'AppURL':
        return self.as_app_url().join(link_text)


@functools.total_ordering
class AppURL:
    """An URL as used internally by Freezeyt.

    An absolute IRI that's "internal" to a given prefix.
    """
    def __init__(
        self,
        str_or_splitresult: Union[str, urllib.parse.SplitResult],
        /,
        prefix: PrefixURL,
    ):
        _url = str_or_splitresult
        split_url: urllib.parse.SplitResult
        if isinstance(str_or_splitresult, str):
            split_url = split_iri(str_or_splitresult)
        else:
            split_url = str_or_splitresult
        split_url = split_url._replace(fragment='')
        if split_url.scheme != prefix.scheme:
            raise ExternalURLError(
                f"External URL: {_url!r} (scheme is not {prefix.scheme!r})")
        if split_url.hostname != prefix.hostname:
            raise ExternalURLError(
                f"External URL: {_url!r} (hostname is not {prefix.hostname!r})")
        if get_port(split_url.port, split_url.scheme) != prefix.port:
            raise ExternalURLError(
                f"External URL: {_url!r} (port is not {prefix.port!r})")
        prefix_path = prefix.path
        app_path = split_url.path
        if app_path.startswith(prefix_path):
            self.relative_path = app_path[len(prefix.path):]
        elif app_path + '/' == prefix_path:
            self.relative_path = ''
        else:
            raise ExternalURLError(
                f"External URL: {_url!r} "
                + f"(path does not start with {prefix_path!r})"
            )
        self._split_url = split_url
        self.prefix = prefix

    def __str__(self):
        return urllib.parse.urlunsplit(self._split_url)

    @property
    def path(self):
        return self._split_url.path

    def join(self, link_text: str) -> 'AppURL':
        """Add a string to the URL, adding a default port for http/https"""
        url_text = urllib.parse.urlunsplit(self._split_url)
        result_text = urllib.parse.urljoin(url_text, uri_to_iri(link_text))
        result = urllib.parse.urlsplit(result_text)
        return AppURL(result, self.prefix)

    @property
    def query(self):
        return self._split_url.query

    @property
    def _key(self):
        return self.relative_path, self.query, self.prefix

    def __eq__(self, other):
        return self._key == other._key

    def __le__(self, other):
        return self._key < other._key

    def __hash__(self):
        return hash(self._key)

    @property
    def port(self):
        return get_port(self._split_url.port, self._split_url.scheme)

    @property
    def relative_path_with_query(self):
        if self.query:
            return self.relative_path + '?' + self.query
        return self.relative_path
