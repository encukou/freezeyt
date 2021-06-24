from freezeyt.getlinks_html import get_all_links


def test_get_links():
    """Test if the get_all_links function returns all links from a page.

    The get_all_links function should return all links
    even when the links are deeper in the page.
    """
    links = get_all_links(b"""
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
    """, 'http://localhost:8000')

    assert sorted(links) == [
        'http://localhost:8000/blabla.png',
        'http://localhost:8000/fourth_page/',
        'http://localhost:8000/second_page',
        'http://localhost:8000/third_page',
    ]


def test_get_links_path():
    links = get_all_links(b"""
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
    """, 'http://localhost:8000/path1/path2/')

    assert sorted(links) == [
        'http://localhost:8000/path1/path2/fourth_page/',
        'http://localhost:8000/second_page',
        'http://localhost:8000/third_page',
    ]


def test_get_links_utf8():
    # Test that links are parsed according to the content encoding (UTF-8)
    links = get_all_links(
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
    )

    assert sorted(links) == [
        'http://localhost:8000/čau',
    ]


def test_get_links_cp1253():
    # Test that links are parsed according to the content encoding (Greek)
    links = get_all_links(
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
    )

    assert sorted(links) == [
        'http://localhost:8000/π',
    ]
