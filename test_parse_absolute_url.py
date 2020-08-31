from pathlib import Path

import pytest

from freezeyt.freezing import parse_absolute_url

def test_absolute():
    with pytest.raises(ValueError):
        parse_absolute_url("/a/b/c")

def test_no_scheme():
    with pytest.raises(ValueError):
        parse_absolute_url("pyladies.cz/")

def test_url_scheme():
    with pytest.raises(ValueError):
        parse_absolute_url("ftp://localhost:8000/second_page.html")

def test_no_port_http():
    parsed = parse_absolute_url("http://pyladies.cz/")
    assert parsed.netloc == 'pyladies.cz:80'

def test_no_port_https():
    parsed = parse_absolute_url("https://naucse.python.cz/")
    assert parsed.netloc == 'naucse.python.cz:443'
