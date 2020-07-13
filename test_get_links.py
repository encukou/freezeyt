from freezeyt import get_all_links

def test_get_links():
    links = get_all_links(b"""
        <html>
            <head>
                <title>Hello world</title>
            </head>
            <body>
                Hello world!
                <br>
                <a href='/second_page'>LINK</a> to second page.
                <a href='/third_page'>LINK</a> to third page.
            </body>
        </html>
    """)

    assert sorted(links) == ['/second_page', '/third_page']
