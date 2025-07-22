from pathlib import PurePosixPath

import pytest

from freezeyt.freezer import get_path_from_url
from freezeyt.urls import PrefixURL, AppURL
import freezeyt


POSITIVE_TEST_CASES = {
    'index': (
        'http://localhost:8000/',
        "http://localhost:8000/",
        "index.html",
    ),
    'second_page': (
        'http://localhost:8000/',
        "http://localhost:8000/second/",
        "second/index.html",
    ),
    'second_page_html': (
        'http://localhost:8000/',
        "http://localhost:8000/second.html",
        "second.html",
    ),
    'fragment': (
        'http://localhost:8000/',
        "http://localhost:8000/second_page.html#odkaz",
        "second_page.html",
    ),
    'custom_prefix_index': (
        'http://freezeyt.test:1234/foo/',
        "http://freezeyt.test:1234/foo/",
        'index.html',
    ),
    'custom_prefix_second_page': (
        'http://freezeyt.test:1234/foo/',
        "http://freezeyt.test:1234/foo/second/",
        "second/index.html",
    ),
    'custom_prefix_second_page_html': (
        'http://freezeyt.test:1234/foo/',
        "http://freezeyt.test:1234/foo/second.html",
        "second.html",
    ),
    'custom_prefix_fragment': (
        'http://freezeyt.test:1234/foo/',
        "http://freezeyt.test:1234/foo/second_page.html#odkaz",
        "second_page.html",
    ),
}

@pytest.mark.parametrize('case', POSITIVE_TEST_CASES)
def test_positive(case):
    prefix_string, url_string, expected = POSITIVE_TEST_CASES[case]
    prefix = PrefixURL(prefix_string)
    result = get_path_from_url(AppURL(url_string, prefix), freezeyt.url_to_path)
    assert result == PurePosixPath(expected)


NEGATIVE_TEST_CASES = {
    'external_page': (
        'http://localhost:8000/',
        "http://python.cz",
    ),
    'scheme_different_ftp': (
        'http://localhost:8000/',
        "ftp://localhost:8000/second_page.html",
    ),
    'scheme_different': (
        'http://localhost:8000/',
        "https://localhost:8000/second_page.html",
    ),
    'relative': (
        'http://localhost:8000/',
        "/a/b/c",
    ),
    'custom_prefix_fragment_ftp': (
        'http://freezeyt.test:1234/foo/',
        "ftp://localhost:8000/second_page.html",
    ),
    'custom_prefix_above': (
        'http://freezeyt.test:1234/foo/',
        "http://freezeyt.test:1234/second_page.html",
    ),
}

@pytest.mark.parametrize('case', NEGATIVE_TEST_CASES)
def test_negative(case):
    prefix_string, url_string = NEGATIVE_TEST_CASES[case]
    prefix = PrefixURL(prefix_string)
    with pytest.raises(ValueError):
        get_path_from_url(AppURL(url_string, prefix), freezeyt.url_to_path)


@pytest.mark.parametrize('bad_input', ['..', 'a/../b', '/a', '//b'])
def test_bad_url_to_path(bad_input):
    def bad_path(path):
        return bad_input

    with pytest.raises(ValueError):
        get_path_from_url(
            PrefixURL('http://localhost:80/').as_app_url(),
            bad_path,
        )

@pytest.mark.parametrize(['input', 'expected'],[
    ('.', '.'),
    ('a/./b', 'a/b'),
])
def test_url_to_path_removes_dots(input, expected):
    def bad_path(path):
        return input

    path = get_path_from_url(
        PrefixURL('http://localhost:80/').as_app_url(),
        bad_path,
    )
    assert str(path) == expected
