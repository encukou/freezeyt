import asyncio
from io import BytesIO
from typing import Dict, Tuple, List

import pytest

from freezeyt.url_finders import get_html_links, get_html_links_async


TEST_DATA: Dict[str, Tuple[Tuple, List[str]]] = {
    'basic': (
        (
            b"""
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
            """,
            'http://localhost:8000',
        ),
        [
            '/second_page',
            '/third_page',
            'blabla.png',
            'fourth_page/',
        ],
    ),
    'path': (
        (
            b"""
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
            """,
            'http://localhost:8000/path1/path2/',
        ),
        [
            '/second_page',
            '/third_page',
            'fourth_page/',
        ],
    ),
    'utf8': (
        (
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
        ),
        ['/čau'],
    ),
    'cp1253': (
        (
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
        ),
        ['/π'],
    ),
    'inline_css': (
        (
            b"""
                <html>
                    <head>
                        <title>Hello world</title>
                        <style>
                            @font-face {
                                font-family: 'TurretRoad';
                                src: url(TurretRoad-Regular.ttf) format('truetype');
                                font-weight: normal;
                            }
                            body {
                                font-family: 'TurretRoad';
                            }
                        </style>
                    </head>
                    <body>
                        This is in a weird font.

                        <p style="background-image: url(smile.png)">
                        </p>
                    </body>
                </html>
            """,
            'http://localhost:8000/',
            {'Content-Type': 'text/html; charset=cp1253'},
        ),
        ['TurretRoad-Regular.ttf', 'smile.png'],
    ),
}


@pytest.mark.parametrize("test_name", TEST_DATA)
def test_links_html(test_name):
    (content, *args), expected = TEST_DATA[test_name]
    f = BytesIO(content)
    links = get_html_links(f, *args)
    assert sorted(links) == expected


@pytest.mark.parametrize("test_name", TEST_DATA)
def test_links_html_async(test_name):
    (content, *args), expected = TEST_DATA[test_name]
    f = BytesIO(content)
    links = asyncio.run(get_html_links_async(f, *args))
    assert sorted(links) == expected
