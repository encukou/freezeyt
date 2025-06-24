import urllib.parse
import functools
from typing import Union

from werkzeug.urls import uri_to_iri

from freezeyt.util import RelativeURLError, UnsupportedSchemeError


@functools.total_ordering
class AbsoluteURL:
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

    @property
    def fragment(self):
        return self._split_url.fragment

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
