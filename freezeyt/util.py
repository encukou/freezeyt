
from urllib.parse import urlparse
from werkzeug.urls import url_parse


def is_external(parsed_url, prefix):
    """Return true if the given URL is within a web app at `prefix`

    Both arguments should be results of urlparse (or parse_absolute_url)
    """
    return (
        parsed_url.scheme != prefix.scheme
        or parsed_url.hostname != prefix.hostname
        or parsed_url.port != prefix.port
        or not parsed_url.path.startswith(prefix.path)
    )


def parse_absolute_url(url):
    """Parse absolute URL

    Returns the same result as urllib.parse.urlparse, but works on
    absolute HTTP and HTTPS URLs only.
    The result port is always an integer.
    """
    parsed = url_parse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Need an absolute URL")

    if parsed.scheme not in ('http', 'https'):
        raise ValueError("URL scheme must be http or https")

    if parsed.port == None:
        if parsed.scheme == 'http':
            parsed = parsed.replace(netloc=parsed.host + ':80')
        elif parsed.scheme == 'https':
            parsed = parsed.replace(netloc=parsed.host + ':443')
        else:
            raise ValueError("URL scheme must be http or https")

    return parsed
    # parsed = urlparse(url)
    # if not parsed.scheme or not parsed.netloc:
    #     raise ValueError("Need an absolute URL")

    # if parsed.scheme not in ('http', 'https'):
    #     raise ValueError("URL scheme must be http or https")

    # if parsed.port == None:
    #     if parsed.scheme == 'http':
    #         parsed = parsed._replace(netloc=parsed.hostname + ':80')
    #     elif parsed.scheme == 'https':
    #         parsed = parsed._replace(netloc=parsed.hostname + ':443')
    #     else:
    #         raise ValueError("URL scheme must be http or https")

    # return parsed
