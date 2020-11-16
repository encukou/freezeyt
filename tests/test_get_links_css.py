from pathlib import Path

from freezeyt.freezing import get_links_from_css


def test_get_links_css():
    css_file = Path(__file__).parent / 'fixtures' / 'css_files' / 'style.css'
    with open(css_file, "rb") as f:
        links = get_links_from_css(f, 'http://localhost:8000')
        assert sorted(links) == ['http://localhost:8000/TurretRoad-Regular.ttf']
