import importlib
import concurrent.futures
import urllib.parse
from typing import Sequence, TYPE_CHECKING, List, Optional, Any
import enum

from werkzeug.urls import uri_to_iri

from freezeyt.compat import _MultiErrorBase, HAVE_EXCEPTION_GROUP
from freezeyt.encoding import decode_input_path
from freezeyt.types import AbsoluteURL


if TYPE_CHECKING:
    from freezeyt.hooks import TaskInfo
    from freezeyt.freezer import Task


process_pool_executor = concurrent.futures.ProcessPoolExecutor()


class InfiniteRedirection(Exception):
    """Infinite redirection was detected with redirect_policy='follow'"""
    def __init__(self, task: 'Task'):
        redirects_to = task.redirects_to
        assert redirects_to is not None
        super().__init__(
            f'{task.get_a_url()} redirects to {redirects_to.get_a_url()},'
            + ' which was not frozen (most likely because of infinite redirection)'
        )

class ExternalURLError(ValueError):
    """Unexpected external URL specified"""

class RelativeURLError(ValueError):
    """Absolute URL was expected"""

class UnsupportedSchemeError(ValueError):
    """Raised for URLs with unsupported schemes"""

class UnexpectedStatus(ValueError):
    """The application returned an unexpected status code for a page"""
    def __init__(self, url: AbsoluteURL, status: str):
        self.url = urllib.parse.urlunsplit(url)
        self.status = status
        message = str(status)
        super().__init__(message)

class WrongMimetypeError(ValueError):
    """MIME type does not match file extension"""
    def __init__(self, expected: List[str], got: str, url_path: str):
        super().__init__(
            f"Content-type {got!r} is different from allowed MIME types {expected}"
            + f" guessed from '{url_path}'"
        )

class MultiError(_MultiErrorBase):
    """Contains multiple errors"""
    tasks: 'Sequence[TaskInfo]'

    if not HAVE_EXCEPTION_GROUP:
        exceptions: Sequence[Exception]

    def __new__(cls, tasks):
        # Import TaskInfo here to avoid a circular import
        # (since hooks imports utils)
        from freezeyt.hooks import TaskInfo

        exceptions = []
        for task in tasks:
            exc = task.asyncio_task.exception()
            exc._freezeyt_exception_task = task
            exceptions.append(exc)

        if HAVE_EXCEPTION_GROUP:
            self = super().__new__(cls, f"{len(tasks)} errors", exceptions)
        else:
            # mypy thinks Exception.__new__ takes only one argument;
            # in reality it passes all its arguments to __init__
            self = super().__new__(cls, f"{len(tasks)} errors") # type: ignore[call-arg]
            self.exceptions = exceptions

        self.tasks = [TaskInfo(t) for t in tasks]
        return self

    def derive(self, excs):
        return MultiError([e._freezeyt_exception_task for e in excs])


class TaskStatus(enum.Enum):
    IN_PROGRESS = "Currently being handled"
    REDIRECTING = "Waiting for target of redirection"
    DONE = "Saved"
    FAILED = "Raised an exception"


def is_external(parsed_url: AbsoluteURL, prefix: AbsoluteURL) -> bool:
    """Return true if the given URL is within a web app at `prefix`
    """
    if parsed_url.scheme not in ('http', 'https'):
        # We know the prefix has a supported scheme.
        # If parsed_url has a different scheme, it must be external.
        return True
    for url in parsed_url, prefix:
        # AbsoluteURL must have port set (for http & https)
        assert url.port is not None
    prefix_path = prefix.path
    if not prefix_path.endswith('/'):
        raise ValueError('prefix must end with /')
    if prefix_path == '/':
        prefix_path = ''

    if (
        parsed_url.scheme != prefix.scheme
        or parsed_url.hostname != prefix.hostname
        or parsed_url.port != prefix.port
        or not parsed_url.path.startswith(prefix_path)
    ):
        # Differing scheme, host, port, or path prefix: URL is external
        return True

    return False


def parse_absolute_url(url: str) -> AbsoluteURL:
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

    parsed = _add_port(parsed)

    return parsed


def _add_port(url: urllib.parse.SplitResult) -> AbsoluteURL:
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
        else:
            raise UnsupportedSchemeError("URL scheme must be http or https")
    return AbsoluteURL(url)


def urljoin(url: AbsoluteURL, link_text: str) -> AbsoluteURL:
    """Add a string to the URL, adding a default port for http/https"""
    url_text = urllib.parse.urlunsplit(url)
    result_text = urllib.parse.urljoin(url_text, uri_to_iri(link_text))
    result = urllib.parse.urlsplit(result_text)
    try:
        return _add_port(result)
    except UnsupportedSchemeError:
        # If this has a scheme other than http and https,
        # it's an external url; we don't need the port in it.
        return AbsoluteURL(result)


def import_variable_from_module(
    name: str,
    *,
    default_module_name: Optional[str] = None,
    default_variable_name: Optional[str] = None,
) -> Any:
    """Import a variable from a named module

    Given a name like "package.module:namespace.variable":
    - import module "package.module"
    - get the attribute "namespace" from the module
    - return the attribute "variable" from the "namespace" object

    Parameter name can be set as module or variable. The missing one
    must be set as default.
    """

    module_name, sep, variable_name = name.partition(':')

    if not sep:
        if default_variable_name:
            if default_module_name:
                raise ValueError(
                        "Both default values can not be used simultaneously"
                        )
            variable_name = default_variable_name
        elif default_module_name:
            module_name, variable_name = default_module_name, module_name

    if not variable_name:
        raise ValueError(f"Missing variable name: {name!r}")

    if not module_name:
        raise ValueError(f"Missing module name: {name!r}")

    module = importlib.import_module(module_name)

    result = module
    for attribute_name in variable_name.split('.'):
        result = getattr(result, attribute_name)

    return result


def get_url_part(part: str) -> str:
    """Get normalized url_part from string.

    Normalizing rules are:
        - decode to unicode
        - any backslash replace by forward slash, except encoded backslash
        - simple dot as filesystem hardlink is removed
        - filesystem hardlink '..' is not allowed
        - multiple slashes reduce to only one
        - relative path does not start with slash
    """

    backslash = "\\"
    part = part.replace(backslash, "/")

    part = decode_input_path(part)

    items = ["" if p == "." else p for p in part.split("/")]

    if ".." in items:
        raise ValueError("'..' component not allowed in URL part")

    part = "/".join(items)

    while "//" in part:
        part = part.replace("//", "/")

    return part.lstrip("/")

