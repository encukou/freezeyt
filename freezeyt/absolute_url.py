import urllib.parse
import functools
from typing import Union

from werkzeug.urls import uri_to_iri

from freezeyt.util import RelativeURLError, UnsupportedSchemeError, BadPrefixError


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
    def __init__(self, url: str):
        split_url: urllib.parse.SplitResult = split_iri(url)
        if not split_url.scheme:
            raise RelativeURLError(f"Expected an absolute URL, not {url}")

        if split_url.scheme not in ('http', 'https'):
            raise UnsupportedSchemeError(f"URL scheme must be http or https: {url}")

        if not split_url.netloc:
            raise RelativeURLError(f"Expected an absolute URL, not {url}")

        if split_url.query:
            raise BadPrefixError("The prefix cannot have a query part")

        if split_url.fragment:
            raise BadPrefixError("The prefix cannot have a fragment part")

        if not split_url.path.endswith('/'):
            raise BadPrefixError("The prefix must end with a slash")

        self._split_url = split_url

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
    def path(self):
        return self._split_url.path


class AppURL:
    """An URL as used internally by Freezeyt.

    An IRI relative to a given prefix.
    """
    def __init__(self, url: str, prefix: PrefixURL):
        split_url: urllib.parse.SplitResult = split_iri(url)
        if split_url.scheme != prefix.scheme:
            raise ExternalURLError(
                f"External URL: {url!r} (scheme is not {prefix.scheme!r})")
        if split_url.hostname != prefix.hostname:
            raise ExternalURLError(
                f"External URL: {url!r} (hostname is not {prefix.hostname!r})")
        if get_port(split_url.port, split_url.scheme) != prefix.port:
            raise ExternalURLError(
                f"External URL: {url!r} (port is not {prefix.port!r})")
        prefix_path = prefix.path
        if prefix_path == '/':
            prefix_path = ''
        if not split_url.path.startswith(prefix_path):
            raise ExternalURLError(
                f"External URL: {url!r} (path does not start with {prefix_path!r})")
        self._split_url = split_url



def _add_port(url: urllib.parse.SplitResult) -> urllib.parse.SplitResult:
    """Returns url with the port set, using the default for HTTP or HTTPS scheme

    `url` must be
        - an absolute IRI, that is, the result of
        urllib.parse.urlsplit(werkzeug.urls.uri_to_iri(...)), or
        - a non-http/https URL, such as `mailto:...` (we don't add the port
        for those).
    """
    if url.port == None:
        if url.scheme == 'http':
            assert url.hostname is not None, f"{url} must be absolute"
            url = url._replace(netloc=url.hostname + ':80')
        elif url.scheme == 'https':
            assert url.hostname is not None, f"{url} must be absolute"
            url = url._replace(netloc=url.hostname + ':443')
    return url

@functools.total_ordering
class xxx_AbsoluteURL:
    """An URL as used internally by Freezeyt.

    Absolute IRI, with an explicit port if it's `http` or `https`, and with
    no fragment.

    AbsoluteURL can be created (parsed) from a string, in which case only
    `http` or `https` URLs are accepted.

    Alternately, it can be created from a urllib.parse.SplitResult, or
    with the join() method. In this case, any scheme is accepted.
    """
    _split_url: urllib.parse.SplitResult

    def __init__(self, split_url: Union[str, urllib.parse.SplitResult]):
        if isinstance(split_url, str):
            _split_url = self._parse_string(split_url)
        else:
            _split_url = split_url
        self._split_url = self._add_port(_split_url)
        self._split_url = self._split_url._replace(fragment='')

    def __str__(self):
        return urllib.parse.urlunsplit(self._split_url)

    def __eq__(self, other):
        return self._split_url == other._split_url

    def __le__(self, other):
        return self._split_url < other._split_url

    def __hash__(self):
        return hash(self._split_url)

    @property
    def scheme(self):
        return self._split_url.scheme

    @property
    def netloc(self):
        return self._split_url.netloc

    @property
    def hostname(self):
        return self._split_url.hostname

    @property
    def port(self):
        return self._split_url.port

    @property
    def path(self):
        return self._split_url.path

    @property
    def query(self):
        return self._split_url.query

    def _replace(self, **kwargs):
        return AbsoluteURL(self._split_url._replace(**kwargs))

    def is_external_to(self, prefix: 'AbsoluteURL') -> bool:
        """Return true if the given URL is within a web app at `prefix`
        """
        parsed_split = self._split_url
        prefix_split = prefix._split_url

        if parsed_split.scheme not in ('http', 'https'):
            # We know the prefix has a supported scheme.
            # If self has a different scheme, it must be external.
            return True
        for url in parsed_split, prefix_split:
            # AbsoluteURL must have port set (for http & https)
            assert url.port is not None
        prefix_path = prefix_split.path
        if not prefix_path.endswith('/'):
            raise ValueError('prefix must end with /')
        if prefix_path == '/':
            prefix_path = ''

        if (
            parsed_split.scheme != prefix_split.scheme
            or parsed_split.hostname != prefix_split.hostname
            or parsed_split.port != prefix_split.port
            or not parsed_split.path.startswith(prefix_path)
        ):
            # Differing scheme, host, port, or path prefix: URL is external
            return True

        return False

    @classmethod
    def _parse_string(cls, url: str) -> urllib.parse.SplitResult:
        """Parse absolute URL

        Returns the same result as urllib.parse.urlsplit, but works on
        absolute HTTP and HTTPS URLs only.
        The result port is always an integer.
        """
        parsed = urllib.parse.urlsplit(uri_to_iri(url))
        if not parsed.scheme:
            raise RelativeURLError(f"Expected an absolute URL, not {url}")

        if parsed.scheme not in ('http', 'https'):
            raise UnsupportedSchemeError(f"URL scheme must be http or https: {url}")

        if not parsed.netloc:
            raise RelativeURLError(f"Expected an absolute URL, not {url}")

        return parsed

    @classmethod
    def _add_port(cls, url: urllib.parse.SplitResult) -> urllib.parse.SplitResult:
        """Returns url with the port set, using the default for HTTP or HTTPS scheme

        `url` must be
            - an absolute IRI, that is, the result of
            urllib.parse.urlsplit(werkzeug.urls.uri_to_iri(...)), or
            - a non-http/https URL, such as `mailto:...` (we don't add the port
            for those).
        """
        if url.port == None:
            if url.scheme == 'http':
                assert url.hostname is not None, f"{url} must be absolute"
                url = url._replace(netloc=url.hostname + ':80')
            elif url.scheme == 'https':
                assert url.hostname is not None, f"{url} must be absolute"
                url = url._replace(netloc=url.hostname + ':443')
        return url

    def join(self, link_text: str) -> 'AbsoluteURL':
        """Add a string to the URL, adding a default port for http/https"""
        url_text = urllib.parse.urlunsplit(self._split_url)
        result_text = urllib.parse.urljoin(url_text, uri_to_iri(link_text))
        result = urllib.parse.urlsplit(result_text)
        return AbsoluteURL(result)
