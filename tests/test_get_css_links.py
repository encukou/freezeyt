from io import BytesIO

import pytest

from freezeyt.getlinks_css import get_links_from_css

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
        ['http://localhost:8000/TurretRoad-Regular.ttf'],
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
            'http://localhost:8000/TurretRoad-Regular.ttf',
            'http://localhost:8000/some-image.png'
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
        ['http://localhost:8000/static/style.css']
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
            'http://localhost:8000/TurretRoad-Regular.ttf',
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
    links = get_links_from_css(f, 'http://localhost:8000')
    assert sorted(links) == expected
