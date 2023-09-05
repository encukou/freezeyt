from urllib.parse import urlsplit

import pytest

from freezeyt.util import is_external, parse_absolute_url


def test_is_external_positive():
    assert not is_external(
        parse_absolute_url('http://localhost:80/a/b/c'),
        parse_absolute_url('http://localhost:80/a/'),
    )


def test_is_external_negative():
    assert is_external(
        parse_absolute_url('http://example.com:80/a/'),
        parse_absolute_url('http://localhost:80/a/b/c/'),
    )


def test_is_external_negative_same_host():
    assert is_external(
        parse_absolute_url('http://localhost:80/a/'),
        parse_absolute_url('http://localhost:80/a/b/c/'),
    )


def test_is_external_same():
    assert not is_external(
        parse_absolute_url('http://localhost:80/a/'),
        parse_absolute_url('http://localhost:80/a/'),
    )


def test_is_external_index():
    assert is_external(
        parse_absolute_url('http://localhost:80/a'),
        parse_absolute_url('http://localhost:80/a/'),
    )


def test_is_external_root_index():
    assert not is_external(
        parse_absolute_url('http://localhost:80'),
        parse_absolute_url('http://localhost:80/'),
    )


def test_is_external_needs_port():
    # `is_external` takes AbsoluteURL, which needs a port set.
    # If we feed it a raw urlsplit result, it'll raise AssertionError.
    with pytest.raises(AssertionError):
        is_external(
            urlsplit('http://localhost/a/'), # type: ignore[arg-type]
            parse_absolute_url('http://localhost:80/a/'),
        )
    with pytest.raises(AssertionError):
        is_external(
            parse_absolute_url('http://localhost:80/a/'),
            urlsplit('http://localhost/a/'),  # type: ignore[arg-type]
        )


def test_is_external_relative():
    with pytest.raises(AssertionError):
        is_external(
            parse_absolute_url('http://localhost:80/a/'),
            urlsplit('/a/'), # type: ignore[arg-type]
        )
