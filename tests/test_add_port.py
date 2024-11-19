from urllib.parse import urlsplit, urlunsplit, urljoin

import pytest

from freezeyt.util import AbsoluteURL

url_with_port = AbsoluteURL('http://localhost:80/')

# To construct URLs without ports, we use urllib.parse.urljoin.
# (The parse_absolute_url function always adds a port.)
def _join(url1: AbsoluteURL, url2_text: str):
    url1_text = str(url1)
    joined_text = urljoin(url1_text, url2_text)
    return urlsplit(joined_text)


def test_add_http_port():
    tested_url = _join(url_with_port, 'http://localhost/')
    assert urlunsplit(tested_url) == 'http://localhost/'
    assert str(AbsoluteURL(tested_url)) == 'http://localhost:80/'

def test_add_https_port():
    tested_url = _join(url_with_port, 'https://localhost/')
    assert urlunsplit(tested_url) == 'https://localhost/'
    assert str(AbsoluteURL(tested_url)) == 'https://localhost:443/'

def test_add_port_unknown_scheme():
    tested_url = _join(url_with_port, 'unknownscheme://localhost/')
    assert urlunsplit(tested_url) == 'unknownscheme://localhost/'
    assert str(AbsoluteURL(tested_url)) == 'unknownscheme://localhost/'

def test_no_add_http_port():
    tested_url = _join(url_with_port, 'http://localhost:1234/')
    assert urlunsplit(tested_url) == 'http://localhost:1234/'
    assert str(AbsoluteURL(tested_url)) == 'http://localhost:1234/'

def test_no_add_https_port():
    tested_url = _join(url_with_port, 'https://localhost:1234/')
    assert urlunsplit(tested_url) == 'https://localhost:1234/'
    assert str(AbsoluteURL(tested_url)) == 'https://localhost:1234/'
