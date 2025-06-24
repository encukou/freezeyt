from freezeyt.absolute_url import PrefixURL, AppURL


def is_external(url, prefix):
    return url.is_external_to(prefix)


def test_is_external_positive():
    assert not is_external(
        AbsoluteURL('http://localhost:80/a/b/c'),
        AbsoluteURL('http://localhost:80/a/'),
    )


def test_is_external_negative():
    assert is_external(
        AbsoluteURL('http://example.com:80/a/'),
        AbsoluteURL('http://localhost:80/a/b/c/'),
    )


def test_is_external_negative_same_host():
    assert is_external(
        AbsoluteURL('http://localhost:80/a/'),
        AbsoluteURL('http://localhost:80/a/b/c/'),
    )


def test_is_external_same():
    assert not is_external(
        AbsoluteURL('http://localhost:80/a/'),
        AbsoluteURL('http://localhost:80/a/'),
    )


def test_is_external_index():
    assert is_external(
        AbsoluteURL('http://localhost:80/a'),
        AbsoluteURL('http://localhost:80/a/'),
    )


def test_is_external_root_index():
    assert not is_external(
        AbsoluteURL('http://localhost:80'),
        AbsoluteURL('http://localhost:80/'),
    )
