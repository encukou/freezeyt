import pytest

from freezeyt.util import parse_absolute_url, add_port

url_with_port = parse_absolute_url('http://localhost:80/')

# To construct URLs without ports, we use "url_with_port.join".
# The parse_absolute_url function always adds a port.


def test_add_http_port():
    tested_url = url_with_port.join('http://localhost/')
    assert tested_url.to_url() == 'http://localhost/'
    assert add_port(tested_url).to_url() == 'http://localhost:80/'

def test_add_https_port():
    tested_url = url_with_port.join('https://localhost/')
    assert tested_url.to_url() == 'https://localhost/'
    assert add_port(tested_url).to_url() == 'https://localhost:443/'

def test_add_port_unknown_scheme():
    tested_url = url_with_port.join('unknownscheme://localhost/')
    assert tested_url.to_url() == 'unknownscheme://localhost/'
    with pytest.raises(ValueError):
        add_port(tested_url)

def test_no_add_http_port():
    tested_url = url_with_port.join('http://localhost:1234/')
    assert tested_url.to_url() == 'http://localhost:1234/'
    assert add_port(tested_url).to_url() == 'http://localhost:1234/'

def test_no_add_https_port():
    tested_url = url_with_port.join('https://localhost:1234/')
    assert tested_url.to_url() == 'https://localhost:1234/'
    assert add_port(tested_url).to_url() == 'https://localhost:1234/'
