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
