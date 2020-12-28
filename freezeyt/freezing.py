from urllib.parse import urlparse, urljoin
from pathlib import Path
from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header
from mimetypes import guess_type
import xml.dom.minidom
import sys
import html5lib
import cssutils

from freezeyt.encoding import decode_input_path, encode_wsgi_path
from freezeyt.encoding import encode_file_path


def parse_absolute_url(url):
    """Parse absolute URL

    Returns the same result as urllib.parse.urlparse, but works on
    absolute HTTP and HTTPS URLs only.
    The result port is always an integer.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Need an absolute URL")

    if parsed.scheme not in ('http', 'https'):
        raise ValueError("URL scheme must be http or https")

    if parsed.port == None:
        if parsed.scheme == 'http':
            parsed = parsed._replace(netloc=parsed.hostname + ':80')
        elif parsed.scheme == 'https':
            parsed = parsed._replace(netloc=parsed.hostname + ':443')
        else:
            raise ValueError("URL scheme must be http or https")

    return parsed


def get_all_links(
    page_content: bytes, base_url, headers: Headers = None
) -> list:
    """Get all links from "page_content".

    Return an iterable of strings.

    base_url is the URL of the page.
    """
    if headers == None:
        cont_charset = None
    else:
        content_type_header = headers.get('Content-Type')
        cont_type, cont_options = parse_options_header(content_type_header)
        cont_charset = cont_options.get('charset')
    document = html5lib.parse(page_content, transport_encoding=cont_charset)
    return get_links_from_node(document, base_url)


def get_links_from_node(node: xml.dom.minidom.Node, base_url) -> list:
    """Get all links from xml.dom.minidom Node."""
    result = []
    if 'href' in node.attrib:
        href = decode_input_path(node.attrib['href'])
        full_url = urljoin(base_url, href)
        result.append(full_url)
    if 'src' in node.attrib:
        href = decode_input_path(node.attrib['src'])
        full_url = urljoin(base_url, href)
        result.append(full_url)
    for child in node:
        result.extend(get_links_from_node(child, base_url))
    return result

def check_mimetype(filename, headers):
    f_type, f_encode = guess_type(str(filename))
    if not f_type:
        f_type = 'application/octet-stream'
    headers = Headers(headers)
    cont_type, cont_encode = parse_options_header(headers.get('Content-Type'))
    if f_type.lower() != cont_type.lower():
        raise ValueError(
            f"Content-type '{cont_type}' is different from filetype '{f_type}'"
            + f" guessed from '{filename}'"
        )


def get_links_from_css(css_file, base_url):
    """Get all links from a CSS file."""
    result = []
    text = css_file.read()
    parsed = cssutils.parseString(text)
    all_urls = cssutils.getUrls(parsed)
    for url in all_urls:
        result.append(urljoin(base_url, url))
    return result
