import pytest

from freezeyt import RelativeURLError
from freezeyt.util import parse_absolute_url

def test_absolute():
    with pytest.raises(RelativeURLError):
        parse_absolute_url("/a/b/c")

def test_no_scheme():
    with pytest.raises(RelativeURLError):
        parse_absolute_url("pyladies.cz/")

def test_no_netloc():
    with pytest.raises(RelativeURLError):
        parse_absolute_url("pyladies.cz/foo")

def test_url_scheme():
    """Absolute URLs with bad scheme raise ValueError, but not RelativeURLError
    """
    with pytest.raises(ValueError):
        try:
            parse_absolute_url("ftp://localhost:8000/second_page.html")
        except RelativeURLError:
            raise AssertionError('should not raise RelativeURLError')

def test_no_port_http():
    parsed = parse_absolute_url("http://pyladies.cz/")
    assert parsed.netloc == 'pyladies.cz:80'

def test_no_port_https():
    parsed = parse_absolute_url("https://naucse.python.cz/")
    assert parsed.netloc == 'naucse.python.cz:443'

def test_netloc():
    parsed = parse_absolute_url("http://freezeyt.test:1234/foo/")
    assert parsed.hostname == 'freezeyt.test'
    assert parsed.port == 1234
    assert parsed.netloc == 'freezeyt.test:1234'

def test_scheme():
    parsed = parse_absolute_url("https://freezeyt.test:1234/foo/")
    assert parsed.scheme == 'https'

def test_path():
    parsed = parse_absolute_url("https://freezeyt.test:1234/foo/")
    assert parsed.path == '/foo/'

def test_query():
    parsed = parse_absolute_url("https://freezeyt.test:1234/foo/?a=123")
    assert parsed.query == 'a=123'

def test_fragment():
    parsed = parse_absolute_url("https://freezeyt.test:1234/foo/#heading")
    assert parsed.fragment == 'heading'

def test_unicode_host():
    parsed = parse_absolute_url("https://čau☺フ.даль.рф:1234/foo/")
    assert parsed.hostname == 'čau☺フ.даль.рф'
