import asyncio
from io import BytesIO

import pytest

from freezeyt.url_finders import get_css_links, get_css_links_async

TEST_DATA = {
    "basic": (
        b"""
            @font-face {
                font-family: 'TurretRoad';
                src: url(TurretRoad-Regular.ttf) format('truetype');
                font-weight: normal;
            }

            body {
                font-family: 'TurretRoad';
            }
        """,
        ['TurretRoad-Regular.ttf'],
    ),
    "two_links": (
        b"""
            @font-face {
                font-family: 'TurretRoad';
                src: url(TurretRoad-Regular.ttf) format('truetype');
                font-weight: normal;
            }

            body {
                font-family: 'TurretRoad';
                background-image: url('some-image.png');
            }
        """,
        [
            'TurretRoad-Regular.ttf',
            'some-image.png'
        ],
    ),
    "without_links": (
        b"""
            body {
                background-color: #C2F5FF;
            }
        """,
        [],
    ),
    "static": (
        b"""
            @import url('static/style.css');
            body {
                background-color: #C2F5FF;
            }
        """,
        ['static/style.css']
    ),
    "one_external": (
        b"""
            @font-face {
                font-family: 'TurretRoad';
                src: url(TurretRoad-Regular.ttf) format('truetype');
                font-weight: normal;
            }

            body {
                font-family: 'TurretRoad';
                background-image: url('https://www.example.com/some-image.png');
            }
        """,
        [
            'TurretRoad-Regular.ttf',
            'https://www.example.com/some-image.png'
        ]
    ),
    "all_external": (
        b"""
            @import url('https://www.example.com/style.css');

            body {
                background-image: url('https://www.example.com/some-image.png');
            }
        """,
        [
            'https://www.example.com/some-image.png',
            'https://www.example.com/style.css'
        ],
    ),
}

@pytest.mark.parametrize("test_name", TEST_DATA)
def test_links_css(test_name):
    input, expected = TEST_DATA[test_name]
    f = BytesIO(input)
    links = get_css_links(f, 'http://localhost:8000')
    assert sorted(links) == expected

@pytest.mark.parametrize("test_name", TEST_DATA)
def test_links_css_async(test_name):
    input, expected = TEST_DATA[test_name]
    f = BytesIO(input)
    links = asyncio.run(get_css_links_async(f, 'http://localhost:8000'))
    assert sorted(links) == expected
