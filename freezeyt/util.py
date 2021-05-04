import importlib

from werkzeug.urls import url_parse


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
        raise ValueError("Need an absolute URL")

    if parsed.scheme not in ('http', 'https'):
        raise ValueError("URL scheme must be http or https")

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

def import_variable_from_module(name, *, default_variable_name=None):
    """Import a variable from a named module

    Given a name like "package.module:namespace.variable":
    - import module "package.module"
    - get the attribute "namespace" from the module
    - return the attribute "variable" from the "namespace" object
    """
    module_name, sep, variable_name = name.partition(':')
    if not sep:
        variable_name = default_variable_name
    if not variable_name:
        raise ValueError(f'Missing variable name: {name!r}')

    module = importlib.import_module(module_name)

    result = module
    for attribute_name in variable_name.split('.'):
        result = getattr(result, attribute_name)

    return result
