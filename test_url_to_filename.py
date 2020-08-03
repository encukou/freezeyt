from pathlib import Path

import pytest

from freezeyt.freezing import url_to_filename

base = Path('/test/')


def test_index():
    assert url_to_filename(base, "/") == base / "index.html"


def test_second_page_html():
    result = url_to_filename(base, "/second_page.html")
    assert result == base / "second_page.html"


def test_second_page():
    result = url_to_filename(base, "/second/")
    assert result == base / "second/index.html"


def test_absolute():
    result = url_to_filename(base, "http://localhost:8000/")
    assert result == base / "index.html"


def test_absolute_html():
    result = url_to_filename(base, "http://localhost:8000/second.html")
    assert result == base / "second.html"


def test_external_page():
    with pytest.raises(ValueError):
        url_to_filename(base, "http://python.cz")


def test_fragment():
    result = url_to_filename(base, "second_page.html#odkaz")
    assert result == base / "second_page.html"


def test_fragment_absolute():
    result = url_to_filename(base, "http://localhost:8000/second_page.html#odkaz")
    assert result == base / "second_page.html"


def test_fragment_ftp():
    with pytest.raises(ValueError):
        url_to_filename(base, "ftp://localhost:8000/second_page.html")
