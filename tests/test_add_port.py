import pytest

from freezeyt.util import parse_absolute_url, add_port

url_with_port = parse_absolute_url('http://localhost:80/')

def test_add_http_port():
    url_without_port = url_with_port.join('http://localhost/')
    assert url_without_port.to_url() == 'http://localhost/'
    assert add_port(url_without_port).to_url() == 'http://localhost:80/'

def test_add_https_port():
    url_without_port = url_with_port.join('https://localhost/')
    assert url_without_port.to_url() == 'https://localhost/'
    assert add_port(url_without_port).to_url() == 'https://localhost:443/'

def test_add_port_unknown_scheme():
    url_without_port = url_with_port.join('unknownscheme://localhost/')
    assert url_without_port.to_url() == 'unknownscheme://localhost/'
    with pytest.raises(ValueError):
        add_port(url_without_port)

def test_no_add_http_port():
    url_without_port = url_with_port.join('http://localhost:1234/')
    assert url_without_port.to_url() == 'http://localhost:1234/'
    assert add_port(url_without_port).to_url() == 'http://localhost:1234/'

def test_no_add_https_port():
    url_without_port = url_with_port.join('https://localhost:1234/')
    assert url_without_port.to_url() == 'https://localhost:1234/'
    assert add_port(url_without_port).to_url() == 'https://localhost:1234/'
