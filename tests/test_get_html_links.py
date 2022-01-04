from freezeyt.url_finders import get_html_links
from freezeyt.compat import asyncio_run


def test_get_links():
    """Test if the get_html_links function returns all links from a page.

    The get_html_links function should return all links
    even when the links are deeper in the page.
    """
    links = asyncio_run(get_html_links(b"""
        <html>
            <head>
                <title>Hello world</title>
            </head>
            <body>
                Hello world!
                <br>
                <a href='/second_page'>LINK</a> to second page.
                <p>
                    <a href='/third_page'>LINK</a> to third page.
                </p>
                <a href='fourth_page/'>LINK</a> to fourth page.
                <img src="blabla.png">
            </body>
        </html>
    """, 'http://localhost:8000'))

    assert sorted(links) == [
        '/second_page',
        '/third_page',
        'blabla.png',
        'fourth_page/',
    ]


def test_get_links_path():
    links = asyncio_run(get_html_links(b"""
        <html>
            <head>
                <title>Hello world</title>
            </head>
            <body>
                Hello world!
                <br>
                <a href='/second_page'>LINK</a> to second page.
                <p>
                    <a href='/third_page'>LINK</a> to third page.
                </p>
                <a href='fourth_page/'>LINK</a> to fourth page.
            </body>
        </html>
    """, 'http://localhost:8000/path1/path2/'))

    assert sorted(links) == [
        '/second_page',
        '/third_page',
        'fourth_page/',
    ]


def test_get_links_utf8():
    # Test that links are parsed according to the content encoding (UTF-8)
    links = asyncio_run(get_html_links(
        b"""
            <html>
                <head>
                    <title>Hello world</title>
                </head>
                <body>
                    <a href='/\xc4\x8dau'>LINK</a> to second page.
                </body>
            </html>
        """,
        'http://localhost:8000/',
        {'Content-Type': 'text/html; charset=utf-8'},
    ))

    assert sorted(links) == [
        '/čau',
    ]


def test_get_links_cp1253():
    # Test that links are parsed according to the content encoding (Greek)
    links = asyncio_run(get_html_links(
        b"""
            <html>
                <head>
                    <title>Hello world</title>
                </head>
                <body>
                    <a href='/\xf0'>LINK</a> to second page.
                </body>
            </html>
        """,
        'http://localhost:8000/',
        {'Content-Type': 'text/html; charset=cp1253'},
    ))

    assert sorted(links) == [
        '/π',
    ]
