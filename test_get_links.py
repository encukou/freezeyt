from freezeyt.freezing import get_all_links


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
                <a href='fourth_page/'>LINK</a> to third page.
                <img src="blabla.png">
            </body>
        </html>
    """, 'http://localhost:8000')

    assert sorted(links) == [
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
                <a href='fourth_page/'>LINK</a> to third page.
                <img src="blabla.png">
            </body>
        </html>
    """, 'http://localhost:8000/path1/path2/')

    assert sorted(links) == [
        'http://localhost:8000/path1/path2/fourth_page/',
        'http://localhost:8000/second_page',
        'http://localhost:8000/third_page',
    ]
