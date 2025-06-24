import pytest

from freezeyt import RelativeURLError
from freezeyt.absolute_url import AbsoluteURL

def test_absolute():
    with pytest.raises(RelativeURLError):
        AbsoluteURL("/a/b/c")

def test_no_scheme():
    with pytest.raises(RelativeURLError):
        AbsoluteURL("pyladies.cz/")

def test_no_netloc():
    with pytest.raises(RelativeURLError):
        AbsoluteURL("pyladies.cz/foo")

def test_url_scheme():
    """Absolute URLs with bad scheme raise ValueError, but not RelativeURLError
    """
    with pytest.raises(ValueError):
        try:
            AbsoluteURL("ftp://localhost:8000/second_page.html")
        except RelativeURLError:
            raise AssertionError('should not raise RelativeURLError')

def test_no_port_http():
    parsed = AbsoluteURL("http://pyladies.cz/")
    assert parsed.netloc == 'pyladies.cz:80'

def test_no_port_https():
    parsed = AbsoluteURL("https://naucse.python.cz/")
    assert parsed.netloc == 'naucse.python.cz:443'

def test_netloc():
    parsed = AbsoluteURL("http://freezeyt.test:1234/foo/")
    assert parsed.hostname == 'freezeyt.test'
    assert parsed.port == 1234
    assert parsed.netloc == 'freezeyt.test:1234'

def test_scheme():
    parsed = AbsoluteURL("https://freezeyt.test:1234/foo/")
    assert parsed.scheme == 'https'

def test_path():
    parsed = AbsoluteURL("https://freezeyt.test:1234/foo/")
    assert parsed.path == '/foo/'

def test_query():
    parsed = AbsoluteURL("https://freezeyt.test:1234/foo/?a=123")
    assert parsed.query == 'a=123'

def test_unicode_host():
    parsed = AbsoluteURL("https://čau☺フ.даль.рф:1234/foo/")
    assert parsed.hostname == 'čau☺フ.даль.рф'
