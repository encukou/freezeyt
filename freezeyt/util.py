import importlib
import concurrent.futures

from werkzeug.urls import url_parse


process_pool_executor = concurrent.futures.ProcessPoolExecutor()


class InfiniteRedirection(Exception):
    """Infinite redirection was detected with redirect_policy='follow'"""
    def __init__(self, task):
        super().__init__(
            f'{task.get_a_url()} redirects to {task.redirects_to.get_a_url()},'
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
    def __init__(self, url, status):
        self.url = str(url)
        self.status = status
        message = str(status)
        super().__init__(message)

class WrongMimetypeError(ValueError):
    """MIME type does not match file extension"""
    def __init__(self, expected, got, url_path):
        super().__init__(
            f"Content-type '{got}' is different from filetype '{expected}'"
            + f" guessed from '{url_path}'"
        )

class MultiError(Exception):
    """Contains multiple errors"""
    def __init__(self, tasks):
        # Import TaskInfo here to avoid a circular import
        # (since hooks imports utils)
        from freezeyt.hooks import TaskInfo

        super().__init__(f"{len(tasks)} errors")
        self._tasks = tasks
        self.exceptions = [t.asyncio_task.exception() for t in tasks]
        self.tasks = [TaskInfo(t) for t in tasks]

def is_external(parsed_url, prefix):
    """Return true if the given URL is within a web app at `prefix`

    Both arguments should be results of parse_absolute_url
    """
    for url in parsed_url, prefix:
        if url.port is None:
            raise ValueError(
                f'URL for is_external must have port set; got {url}'
            )
    prefix_path = prefix.path
    if not prefix_path.endswith('/'):
        raise ValueError('prefix must end with /')
    if prefix_path == '/':
        prefix_path = ''
    return (
        parsed_url.scheme != prefix.scheme
        or parsed_url.ascii_host != prefix.ascii_host
        or parsed_url.port != prefix.port
        or not parsed_url.path.startswith(prefix_path)
    )


def parse_absolute_url(url):
    """Parse absolute URL

    Returns the same result as werkzeug.urls.url_parse, but works on
    absolute HTTP and HTTPS URLs only.
    The result port is always an integer.
    """
    parsed = url_parse(url)
    if not parsed.scheme:
        raise RelativeURLError(f"Expected an absolute URL, not {url}")

    if parsed.scheme not in ('http', 'https'):
        raise UnsupportedSchemeError(f"URL scheme must be http or https: {url}")

    if not parsed.netloc:
        raise RelativeURLError(f"Expected an absolute URL, not {url}")

    parsed = add_port(parsed)

    return parsed


def add_port(url):
    """Returns url with the port set, using the default for HTTP or HTTPS scheme"""
    if url.port == None:
        if url.scheme == 'http':
            url = url.replace(netloc=url.host + ':80')
        elif url.scheme == 'https':
            url = url.replace(netloc=url.host + ':443')
        else:
            raise UnsupportedSchemeError("URL scheme must be http or https")
    return url

def import_variable_from_module(
    name, *, default_module_name=None, default_variable_name=None):
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
