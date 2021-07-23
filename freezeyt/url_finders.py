import xml.dom.minidom
from typing import Iterable, BinaryIO
from urllib.parse import urljoin

import html5lib
import css_parser

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header

from freezeyt.encoding import decode_input_path


def get_css_links(
    css_file: BinaryIO, base_url: str, headers: Headers = None
)  -> Iterable[str]:
    """Get all links from a CSS file."""
    result = []
    text = css_file.read()
    parsed = css_parser.parseString(text)
    all_urls = css_parser.getUrls(parsed)
    for url in all_urls:
        result.append(urljoin(base_url, url))
    return result


def get_html_links(
    page_content: bytes, base_url: str, headers: Headers = None
) -> Iterable[str]:
    """Get all links from "page_content".

    Return an iterable of strings.

    base_url is the URL of the page.
    """

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


    if headers == None:
        cont_charset = None
    else:
        content_type_header = Headers(headers).get('Content-Type')
        cont_type, cont_options = parse_options_header(content_type_header)
        cont_charset = cont_options.get('charset')
    document = html5lib.parse(page_content, transport_encoding=cont_charset)
    return get_links_from_node(document, base_url)
