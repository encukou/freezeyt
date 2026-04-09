import xml.etree.ElementTree
from typing import Iterable, BinaryIO, Optional, Callable
from typing import Coroutine, Union, Any, TYPE_CHECKING
import asyncio

import html5lib
import tinycss2
import tinycss2.ast

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header

from .util import process_pool_executor
from .types import WSGIHeaderList


_Headers = Optional[WSGIHeaderList]
UrlFinder = Callable[
    [BinaryIO, str, _Headers],
    Union[Iterable[str], Coroutine[Any, Any, Iterable[str]]],
]


def _get_css_links(
    content: bytes, base_url: str, headers: _Headers,
)  -> Iterable[str]:
    """Get all links from a CSS file."""
    if headers == None:
        cont_charset = None
    else:
        content_type_header = Headers(headers).get('Content-Type')
        cont_type, cont_options = parse_options_header(content_type_header)
        cont_charset = cont_options.get('charset')

    parsed, encoding = tinycss2.parse_stylesheet_bytes(
        content,
        protocol_encoding=cont_charset,
        skip_comments=True,
        skip_whitespace=True,
        # Ideally, we'd set `environment_encoding` to the encoding of the
        # document that included this stylesheet.
        # Freezeyt cannot currently do this easily.
    )
    return list(get_urls_from_tinycss2_value(parsed))


def get_urls_from_tinycss2_value(value: Any) -> Iterable[str]:
    if value is None:
        pass
    elif isinstance(value, (str, int, float)):
        pass
    elif isinstance(value, list):
        for item in value:
            yield from get_urls_from_tinycss2_value(item)
    elif isinstance(value, tinycss2.ast.Node):
        for attr_name in value.__slots__:
            attr_value = getattr(value, attr_name)
            yield from get_urls_from_tinycss2_value(attr_value)
        if isinstance(value, tinycss2.ast.URLToken):
            yield value.value
        if isinstance(value, tinycss2.ast.FunctionBlock):
            if value.name == 'url' and value.arguments:
                arg = value.arguments[0]
                if isinstance(arg, tinycss2.ast.StringToken):
                    yield arg.value
    else:
        raise TypeError(type(value))


def _get_html_links(
    page_content: bytes, base_url: str, headers: _Headers,
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


def get_html_links(
    html_file: BinaryIO, base_url: str, headers: _Headers=None,
) -> Iterable[str]:
    content = html_file.read()
    return _get_html_links(content, base_url, headers)


def get_css_links(
    css_file: BinaryIO, base_url: str, headers: _Headers=None,
)  -> Iterable[str]:
    content = css_file.read()
    return _get_css_links(content, base_url, headers)


async def get_css_links_async(
    css_file: BinaryIO, base_url: str, headers: _Headers=None,
)  -> Iterable[str]:
    loop = asyncio.get_running_loop()
    content = css_file.read()
    return await loop.run_in_executor(
        process_pool_executor, _get_css_links, content, base_url, headers,
    )


async def get_html_links_async(
    html_file: BinaryIO, base_url: str, headers: _Headers=None,
)  -> Iterable[str]:
    loop = asyncio.get_running_loop()
    content = html_file.read()
    return await loop.run_in_executor(
        process_pool_executor, _get_html_links, content, base_url, headers,
    )

def none(
    html_file: BinaryIO, base_url: str, headers: _Headers=None,
)  -> Iterable[str]:
    return []

if TYPE_CHECKING:
    # Check that the default functions have the proper types
    _: UrlFinder
    _ = get_css_links
    _ = get_css_links_async
    _ = get_html_links
    _ = get_html_links_async
    _ = none
