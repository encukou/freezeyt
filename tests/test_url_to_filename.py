from pathlib import Path
from urllib.parse import urlparse

import pytest

from freezeyt.freezer import FileSaver

base = Path('/test/')


def test_index():
    saver = FileSaver(base, urlparse('http://localhost:8000/'))
    assert saver.url_to_filename("http://localhost:8000/") == base / "index.html"


def test_second_page():
    saver = FileSaver(base, urlparse('http://localhost:8000/'))
    result = saver.url_to_filename("http://localhost:8000/second/")
    assert result == base / "second/index.html"


def test_second_page_html():
    saver = FileSaver(base, urlparse('http://localhost:8000/'))
    result = saver.url_to_filename("http://localhost:8000/second.html")
    assert result == base / "second.html"


def test_external_page():
    saver = FileSaver(base, urlparse('http://localhost:8000/'))
    with pytest.raises(ValueError):
        saver.url_to_filename("http://python.cz")


def test_fragment():
    saver = FileSaver(base, urlparse('http://localhost:8000/'))
    result = saver.url_to_filename("http://localhost:8000/second_page.html#odkaz")
    assert result == base / "second_page.html"


def test_scheme_ftp():
    saver = FileSaver(base, urlparse('http://localhost:8000/'))
    with pytest.raises(ValueError):
        saver.url_to_filename("ftp://localhost:8000/second_page.html")


def test_relative():
    saver = FileSaver(base, urlparse('http://localhost:8000/'))
    with pytest.raises(ValueError):
        saver.url_to_filename("/a/b/c")


def test_custom_prefix_index():
    saver = FileSaver(base, urlparse('http://freezeyt.test:1234/foo/'))
    result = saver.url_to_filename("http://freezeyt.test:1234/foo/")
    assert result == base / 'index.html'


def test_custom_prefix_second_page():
    saver = FileSaver(base, urlparse('http://freezeyt.test:1234/foo/'))
    result = saver.url_to_filename("http://freezeyt.test:1234/foo/second/")
    assert result == base / "second/index.html"


def test_custom_prefix_second_page_html():
    saver = FileSaver(base, urlparse('http://freezeyt.test:1234/foo/'))
    result = saver.url_to_filename("http://freezeyt.test:1234/foo/second.html")
    assert result == base / "second.html"


def test_custom_prefix_fragment():
    saver = FileSaver(base, urlparse('http://freezeyt.test:1234/foo/'))
    result = saver.url_to_filename("http://freezeyt.test:1234/foo/second_page.html#odkaz")
    assert result == base / "second_page.html"


def test_custom_prefix_fragment_ftp():
    saver = FileSaver(base, urlparse('http://freezeyt.test:1234/foo/'))
    with pytest.raises(ValueError):
        saver.url_to_filename("ftp://localhost:8000/second_page.html")
