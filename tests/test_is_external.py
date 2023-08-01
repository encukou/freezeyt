from urllib.parse import urlsplit

import pytest

from freezeyt.util import is_external


def test_is_external_positive():
    assert not is_external(
        urlsplit('http://localhost:80/a/b/c'),
        urlsplit('http://localhost:80/a/'),
    )


def test_is_external_negative():
    assert is_external(
        urlsplit('http://example.com:80/a/'),
        urlsplit('http://localhost:80/a/b/c/'),
    )


def test_is_external_negative_same_host():
    assert is_external(
        urlsplit('http://localhost:80/a/'),
        urlsplit('http://localhost:80/a/b/c/'),
    )


def test_is_external_same():
    assert not is_external(
        urlsplit('http://localhost:80/a/'),
        urlsplit('http://localhost:80/a/'),
    )


def test_is_external_index():
    assert is_external(
        urlsplit('http://localhost:80/a'),
        urlsplit('http://localhost:80/a/'),
    )


def test_is_external_root_index():
    assert not is_external(
        urlsplit('http://localhost:80'),
        urlsplit('http://localhost:80/'),
    )


def test_is_external_no_port():
    with pytest.raises(ValueError):
        is_external(
            urlsplit('http://localhost/a/'),
            urlsplit('http://localhost:80/a/'),
        )
    with pytest.raises(ValueError):
        is_external(
            urlsplit('http://localhost:80/a/'),
            urlsplit('http://localhost/a/'),
        )


def test_is_external_relative():
    with pytest.raises(ValueError):
        is_external(
            urlsplit('http://localhost:80/a/'),
            urlsplit('/a/'),
        )
