import pytest

from freezeyt.util import is_external
from werkzeug.urls import url_parse


def test_is_external_positive():
    assert not is_external(
        url_parse('http://localhost:80/a/b/c'),
        url_parse('http://localhost:80/a/'),
    )


def test_is_external_negative():
    assert is_external(
        url_parse('http://example.com:80/a/'),
        url_parse('http://localhost:80/a/b/c/'),
    )


def test_is_external_negative_same_host():
    assert is_external(
        url_parse('http://localhost:80/a/'),
        url_parse('http://localhost:80/a/b/c/'),
    )


def test_is_external_same():
    assert not is_external(
        url_parse('http://localhost:80/a/'),
        url_parse('http://localhost:80/a/'),
    )


def test_is_external_index():
    assert is_external(
        url_parse('http://localhost:80/a'),
        url_parse('http://localhost:80/a/'),
    )


def test_is_external_root_index():
    assert not is_external(
        url_parse('http://localhost:80'),
        url_parse('http://localhost:80/'),
    )


def test_is_external_no_port():
    with pytest.raises(ValueError):
        is_external(
            url_parse('http://localhost/a/'),
            url_parse('http://localhost:80/a/'),
        )
    with pytest.raises(ValueError):
        is_external(
            url_parse('http://localhost:80/a/'),
            url_parse('http://localhost/a/'),
        )
