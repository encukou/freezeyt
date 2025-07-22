import pytest

from freezeyt import RelativeURLError
from freezeyt.urls import PrefixURL
from freezeyt.util import BadPrefixError

def test_absolute():
    with pytest.raises(RelativeURLError):
        PrefixURL("/a/b/c")

def test_no_scheme():
    with pytest.raises(RelativeURLError):
        PrefixURL("pyladies.cz/")

def test_no_netloc():
    with pytest.raises(RelativeURLError):
        PrefixURL("pyladies.cz/foo")

def test_url_scheme():
    """Absolute URLs with bad scheme raise ValueError, but not RelativeURLError
    """
    with pytest.raises(ValueError):
        try:
            PrefixURL("ftp://localhost:8000/second_page.html")
        except RelativeURLError:
            raise AssertionError('should not raise RelativeURLError')

def test_no_port_http():
    parsed = PrefixURL("http://pyladies.cz/")
    assert parsed.netloc == 'pyladies.cz'
    assert parsed.hostname == 'pyladies.cz'
    assert parsed.port == 80

def test_default_port_http():
    parsed = PrefixURL("http://pyladies.cz:80/")
    assert parsed.netloc == 'pyladies.cz:80'
    assert parsed.hostname == 'pyladies.cz'
    assert parsed.port == 80

def test_no_port_https():
    parsed = PrefixURL("https://naucse.python.cz/")
    assert parsed.netloc == 'naucse.python.cz'
    assert parsed.hostname == 'naucse.python.cz'
    assert parsed.port == 443

def test_netloc():
    parsed = PrefixURL("http://freezeyt.test:1234/foo/")
    assert parsed.hostname == 'freezeyt.test'
    assert parsed.port == 1234
    assert parsed.netloc == 'freezeyt.test:1234'

def test_scheme():
    parsed = PrefixURL("https://freezeyt.test:1234/foo/")
    assert parsed.scheme == 'https'

def test_path():
    parsed = PrefixURL("https://freezeyt.test:1234/foo/")
    assert parsed.path == '/foo/'

def test_query():
    with pytest.raises(BadPrefixError):
        PrefixURL("https://freezeyt.test:1234/foo/?a=123")

def test_unicode_host():
    parsed = PrefixURL("https://čau☺フ.даль.рф:1234/foo/")
    assert parsed.hostname == 'čau☺フ.даль.рф'

def test_no_slash():
    with pytest.raises(BadPrefixError):
        PrefixURL("http://pyladies.cz")
