from pathlib import PurePosixPath
from werkzeug.urls import url_parse

import pytest

from freezeyt.freezer import url_to_path


def test_index():
    prefix = url_parse('http://localhost:8000/')
    result = url_to_path(prefix, url_parse("http://localhost:8000/"))
    assert result == PurePosixPath("index.html")


def test_second_page():
    prefix = url_parse('http://localhost:8000/')
    result = url_to_path(prefix, url_parse("http://localhost:8000/second/"))
    assert result == PurePosixPath("second/index.html")


def test_second_page_html():
    prefix = url_parse('http://localhost:8000/')
    result = url_to_path(prefix,url_parse("http://localhost:8000/second.html"))
    assert result == PurePosixPath("second.html")


def test_external_page():
    prefix = url_parse('http://localhost:8000/')
    with pytest.raises(ValueError):
        url_to_path(prefix, url_parse("http://python.cz"))


def test_fragment():
    prefix = url_parse('http://localhost:8000/')
    result = url_to_path(prefix, url_parse("http://localhost:8000/second_page.html#odkaz"))
    assert result == PurePosixPath("second_page.html")


def test_scheme_different_ftp():
    prefix = url_parse('http://localhost:8000/')
    with pytest.raises(ValueError):
        url_to_path(prefix, url_parse("ftp://localhost:8000/second_page.html"))


def test_scheme_different():
    prefix = url_parse('http://localhost:8000/')
    with pytest.raises(ValueError):
        url_to_path(prefix, url_parse("https://localhost:8000/second_page.html"))


def test_relative():
    prefix = url_parse('http://localhost:8000/')
    with pytest.raises(ValueError):
        url_to_path(prefix, url_parse("/a/b/c"))


def test_custom_prefix_index():
    prefix = url_parse('http://freezeyt.test:1234/foo/')
    result = url_to_path(prefix, url_parse("http://freezeyt.test:1234/foo/"))
    assert result == PurePosixPath('index.html')


def test_custom_prefix_second_page():
    prefix = url_parse('http://freezeyt.test:1234/foo/')
    result = url_to_path(prefix, url_parse("http://freezeyt.test:1234/foo/second/"))
    assert result == PurePosixPath("second/index.html")


def test_custom_prefix_second_page_html():
    prefix = url_parse('http://freezeyt.test:1234/foo/')
    result = url_to_path(prefix, url_parse("http://freezeyt.test:1234/foo/second.html"))
    assert result == PurePosixPath("second.html")


def test_custom_prefix_fragment():
    prefix = url_parse('http://freezeyt.test:1234/foo/')
    result = url_to_path(prefix, url_parse("http://freezeyt.test:1234/foo/second_page.html#odkaz"))
    assert result == PurePosixPath("second_page.html")


def test_custom_prefix_fragment_ftp():
    prefix = url_parse('http://freezeyt.test:1234/foo/')
    with pytest.raises(ValueError):
        url_to_path(prefix, url_parse("ftp://localhost:8000/second_page.html"))


def test_custom_prefix_above():
    prefix = url_parse('http://freezeyt.test:1234/foo/')
    with pytest.raises(ValueError):
        url_to_path(prefix, url_parse("http://freezeyt.test:1234/second_page.html"))
