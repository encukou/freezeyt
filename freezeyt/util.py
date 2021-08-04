import importlib

from werkzeug.urls import url_parse


class InfiniteRedirection(Exception):
    """Infinite redirection was detected with redirect_policy='follow'"""
    def __init__(self, task):
        super().__init__(
            f'{task.get_a_url()} redirects to {task.redirects_to.get_a_url()},'
            + ' which was not frozen (most likely becaus of infinite redirection)'
        )

class ExternalURLError(ValueError):
    """Unexpected external URL specified"""

class RelativeURLError(ValueError):
    """Absolute URL was expected"""

class UnexpectedStatus(ValueError):
    """The application returned an unexpected status code for a page"""
    def __init__(self, url, status):
        self.url = url
        self.status = status
        super().__init__(f"Unexpected status '{status}' on URL {url.to_url()}")

class WrongMimetypeError(ValueError):
    """MIME type does not match file extension"""
    def __init__(self, expected, got, url_path):
        super().__init__(
            f"Content-type '{got}' is different from filetype '{expected}'"
            + f" guessed from '{url_path}'"
        )

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
    if not parsed.scheme or not parsed.netloc:
        raise RelativeURLError(f"Expected an absolute URL, not {url}")

    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"URL scheme must be http or https: {url}")

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
            raise ValueError("URL scheme must be http or https")
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
        if default_variable_name is not None:
            variable_name = default_variable_name
        else:
            module_name, variable_name = default_module_name, module_name

    if not variable_name or not module_name:
        raise ValueError(f'Missing variable or module name: {name!r}')

    module = importlib.import_module(module_name)

    result = module
    for attribute_name in variable_name.split('.'):
        result = getattr(result, attribute_name)

    return result
