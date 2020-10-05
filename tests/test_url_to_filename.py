from pathlib import Path

import pytest

from freezeyt.freezing import url_to_filename

base = Path('/test/')


def test_index():
    assert url_to_filename(base, "http://localhost:8000/") == base / "index.html"


def test_second_page():
    result = url_to_filename(base, "http://localhost:8000/second/")
    assert result == base / "second/index.html"


def test_second_page_html():
    result = url_to_filename(base, "http://localhost:8000/second.html")
    assert result == base / "second.html"


def test_external_page():
    with pytest.raises(ValueError):
        url_to_filename(base, "http://python.cz")


def test_fragment():
    result = url_to_filename(base, "http://localhost:8000/second_page.html#odkaz")
    assert result == base / "second_page.html"


def test_scheme_ftp():
    with pytest.raises(ValueError):
        url_to_filename(base, "ftp://localhost:8000/second_page.html")


def test_relative():
    with pytest.raises(ValueError):
        url_to_filename(base, "/a/b/c")


def test_custom_prefix_index():
    result = url_to_filename(
        base, "http://freezeyt.test:1234/foo/",
        hostname='freezeyt.test',
        port=1234,
        path='/foo/',
    )
    assert result == base / 'index.html'


def test_custom_prefix_second_page():
    result = url_to_filename(
        base, "http://freezeyt.test:1234/foo/second/",
        hostname='freezeyt.test',
        port=1234,
        path='/foo/',
    )
    assert result == base / "second/index.html"


def test_custom_prefix_second_page_html():
    result = url_to_filename(
        base, "http://freezeyt.test:1234/foo/second.html",
        hostname='freezeyt.test',
        port=1234,
        path='/foo/',
    )
    assert result == base / "second.html"


def test_custom_prefix_fragment():
    result = url_to_filename(
        base, "http://freezeyt.test:1234/foo/second_page.html#odkaz",
        hostname='freezeyt.test',
        port=1234,
        path='/foo/',
    )
    assert result == base / "second_page.html"


def test_custom_prefix_fragment_ftp():
    with pytest.raises(ValueError):
        url_to_filename(
            base, "ftp://localhost:8000/second_page.html",
            hostname='freezeyt.test',
            port=1234,
            path='/foo/',
        )
