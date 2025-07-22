import pytest

from freezeyt.urls import PrefixURL, AppURL
from freezeyt.util import ExternalURLError

def test_explicit_port():
    prefix = PrefixURL('http://localhost:8000/')
    assert prefix.port == 8000
    assert AppURL('http://localhost:8000/xyz', prefix).port == 8000
    with pytest.raises(ExternalURLError):
        AppURL('http://localhost:80/xyz', prefix)
    with pytest.raises(ExternalURLError):
        AppURL('http://localhost/xyz', prefix)

def test_implicit_port_http():
    prefix = PrefixURL('http://localhost/')
    assert prefix.port == 80
    assert AppURL('http://localhost:80/xyz', prefix).port == 80
    assert AppURL('http://localhost/xyz', prefix).port == 80
    with pytest.raises(ExternalURLError):
        AppURL('http://localhost:8000/xyz', prefix)

def test_implicit_port_https():
    prefix = PrefixURL('https://localhost/')
    assert prefix.port == 443
    assert AppURL('https://localhost:443/xyz', prefix).port == 443
    assert AppURL('https://localhost/xyz', prefix).port == 443
    with pytest.raises(ExternalURLError):
        AppURL('https://localhost:8000/xyz', prefix)


def test_non_external_url():
    url = AppURL('http://localhost:80/a/b/c', PrefixURL('http://localhost:80/a/'))
    assert url.relative_path == 'b/c'


def test_external_url_base():
    with pytest.raises(ExternalURLError):
        AppURL('http://example.com:80/a/', PrefixURL('http://localhost:80/a/b/c/'))


def test_external_url_same_host():
    with pytest.raises(ExternalURLError):
        AppURL('http://localhost:80/a/', PrefixURL('http://localhost:80/a/b/c/'))


def test_non_external_same():
    url = AppURL('http://localhost:80/a/', PrefixURL('http://localhost:80/a/'))
    assert url.relative_path == ''


def test_non_external_index():
    url = AppURL('http://localhost:80', PrefixURL('http://localhost:80/'))
    assert url.relative_path == ''


def test_non_external_index_path():
    url = AppURL('http://localhost:80/a', PrefixURL('http://localhost:80/a/'))
    assert url.relative_path == ''


@pytest.mark.parametrize('prefix_str', [
    'http://localhost/',
    'http://localhost:80/',
    'http://localhost:8000/',
    'http://localhost/a/b/c/',
    'http://localhost:8000/a/b/c/',
    'https://localhost/',
])
def test_as_app_url(prefix_str):
    prefix = PrefixURL(prefix_str)
    assert str(prefix) == prefix_str
    app_url = prefix.as_app_url()
    assert str(app_url) == prefix_str
    assert app_url.relative_path == ''
