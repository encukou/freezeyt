from io import BytesIO

from freezeyt.freezing import get_links_from_css


def test_get_links_css():
    f = BytesIO(b"""
        @font-face {
            font-family: 'TurretRoad';
            src: url(TurretRoad-Regular.ttf) format('truetype');
            font-weight: normal;
        }

        body {
            font-family: 'TurretRoad';
        }
    """)
    links = get_links_from_css(f, 'http://localhost:8000')
    assert sorted(links) == ['http://localhost:8000/TurretRoad-Regular.ttf']


def test_links_css_two_links():
    f = BytesIO(b"""
        @font-face {
            font-family: 'TurretRoad';
            src: url(TurretRoad-Regular.ttf) format('truetype');
            font-weight: normal;
        }

        body {
            font-family: 'TurretRoad';
            background-image: url('some-image.png');
        }
    """)
    links = get_links_from_css(f, 'http://localhost:8000')
    assert sorted(links) == [
        'http://localhost:8000/TurretRoad-Regular.ttf',
        'http://localhost:8000/some-image.png'
    ]


def test_links_css_without_links():
    f = BytesIO(b"""
        body {
            background-color: #C2F5FF;
        }
    """)
    links = get_links_from_css(f, 'http://localhost:8000')
    assert links == []


def test_links_css_static():
    f = BytesIO(b"""
        @import url('static/style.css');
        body {
            background-color: #C2F5FF;
        }
    """)
    links = get_links_from_css(f, 'http://localhost:8000')
    assert sorted(links) == ['http://localhost:8000/static/style.css']


def test_links_css_one_external():
    f = BytesIO(b"""
        @font-face {
            font-family: 'TurretRoad';
            src: url(TurretRoad-Regular.ttf) format('truetype');
            font-weight: normal;
        }

        body {
            font-family: 'TurretRoad';
            background-image: url('https://www.example.com/some-image.png');
        }
    """)
    links = get_links_from_css(f, 'http://localhost:8000')
    assert sorted(links) == [
        'http://localhost:8000/TurretRoad-Regular.ttf',
        'https://www.example.com/some-image.png'
    ]


def test_links_css_all_external():
    f = BytesIO(b"""
        @import url('https://www.example.com/style.css');

        body {
            background-image: url('https://www.example.com/some-image.png');
        }
    """)
    links = get_links_from_css(f, 'http://localhost:8000')
    assert sorted(links) == [
        'https://www.example.com/some-image.png',
        'https://www.example.com/style.css'
    ]
