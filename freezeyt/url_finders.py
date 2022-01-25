import xml.etree.ElementTree
from typing import Iterable, BinaryIO, List, Optional, Tuple

import html5lib
import css_parser

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header

from . import compat


def get_css_links(
    css_file: BinaryIO,
    base_url: str,
    headers: Optional[List[Tuple[str, str]]]=None,
)  -> Iterable[str]:
    """Get all links from a CSS file."""
    text = css_file.read()
    parsed = css_parser.parseString(text)
    return list(css_parser.getUrls(parsed))


def get_html_links(
    page_content: BinaryIO,
    base_url: str,
    headers: Optional[List[Tuple[str, str]]]=None,
) -> Iterable[str]:
    """Get all links from "page_content".

    Return an iterable of strings.

    base_url is the URL of the page.
    """

    def get_links_from_node(
        node: xml.etree.ElementTree.Element,
        base_url: str,
    ) -> Iterable[str]:
        """Get all links from an element."""
        if 'href' in node.attrib:
            yield node.attrib['href']
        if 'src' in node.attrib:
            yield node.attrib['src']
        for child in node:
            yield from get_links_from_node(child, base_url)

    if headers == None:
        cont_charset = None
    else:
        content_type_header = Headers(headers).get('Content-Type')
        cont_type, cont_options = parse_options_header(content_type_header)
        cont_charset = cont_options.get('charset')
    document = html5lib.parse(page_content, transport_encoding=cont_charset)
    return list(get_links_from_node(document, base_url))


async def get_css_links_async(
    css_file: BinaryIO,
    base_url: str,
    headers: Optional[List[Tuple[str, str]]]=None,
)  -> Iterable[str]:
    loop = compat.get_running_loop()
    return await loop.run_in_executor(
        None, get_css_links, css_file, base_url, headers,
    )


async def get_html_links_async(
    page_content: BinaryIO,
    base_url: str,
    headers: Optional[List[Tuple[str, str]]]=None,
)  -> Iterable[str]:
    loop = compat.get_running_loop()
    return await loop.run_in_executor(
        None, get_html_links, page_content, base_url, headers,
    )
