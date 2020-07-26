from freezeyt import get_all_links


def test_get_links():
    """
    Tests if the function gets all links from a page,
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
                <img src="blabla.png">
            </body>
        </html>
    """)

    assert sorted(links) == ['/second_page', '/third_page']
