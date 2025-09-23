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
    return list(get_urls_from_tinycss2_nodes(parsed))

def get_urls_from_tinycss2_nodes(
    nodes: list[tinycss2.ast.Node] | None
) -> Iterable[str]:
    if nodes is None:
        return
    for node in nodes:
        match node:
            case tinycss2.ast.QualifiedRule():
                yield from get_urls_from_tinycss2_nodes(node.prelude)
                yield from get_urls_from_tinycss2_nodes(node.content)
            case tinycss2.ast.AtRule():
                yield from get_urls_from_tinycss2_nodes(node.prelude)
                yield from get_urls_from_tinycss2_nodes(node.content)
            case tinycss2.ast.Declaration():
                yield from get_urls_from_tinycss2_nodes(node.value)
            case tinycss2.ast.ParseError():
                pass
            case tinycss2.ast.Comment():
                pass
            case tinycss2.ast.WhitespaceToken():
                pass
            case tinycss2.ast.LiteralToken():
                pass
            case tinycss2.ast.IdentToken():
                pass
            case tinycss2.ast.AtKeywordToken():
                pass
            case tinycss2.ast.HashToken():
                pass
            case tinycss2.ast.StringToken():
                pass
            case tinycss2.ast.URLToken():
                # TODO: unescape
                yield node.value
            case tinycss2.ast.UnicodeRangeToken():
                pass
            case tinycss2.ast.NumberToken():
                pass
            case tinycss2.ast.PercentageToken():
                pass
            case tinycss2.ast.DimensionToken():
                pass
            case tinycss2.ast.ParenthesesBlock():
                yield from get_urls_from_tinycss2_nodes(node.content)
            case tinycss2.ast.SquareBracketsBlock():
                yield from get_urls_from_tinycss2_nodes(node.content)
            case tinycss2.ast.CurlyBracketsBlock():
                yield from get_urls_from_tinycss2_nodes(node.content)
            case tinycss2.ast.FunctionBlock():
                yield from get_urls_from_tinycss2_nodes(node.arguments)
                if node.name == 'url':
                    match node.arguments:
                        case [tinycss2.ast.StringToken() as string]:
                            # TODO: unescape
                            yield string.value
            case _:
                raise TypeError(node)


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
