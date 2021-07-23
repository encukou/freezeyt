import pytest

from freezeyt import freeze
from freezeyt.freezer import parse_url_finders
from freezeyt.url_finders import get_html_links
from freezeyt.url_finders import get_css_links
from testutil import context_for_test


TEST_DATA = {
    'html_links_fallback':
        (   'text/html',
            {'text/html': 'get_html_links'},
            ('freezeyt.url_finders', 'get_html_links', get_html_links)
        ),
    'css_links_fallback':
        (   'text/css',
            {'text/css': 'get_css_links'},
            ('freezeyt.url_finders', 'get_css_links', get_css_links)
        ),
}


@pytest.mark.parametrize("test_name", TEST_DATA)
def test_parse_url_finders(test_name):
    key, config, expected = TEST_DATA[test_name]
    result = parse_url_finders(config)[key]

    assert (result.__module__, result.__name__, result) == expected


def test_get_no_url_finders():
    config = {}
    result = parse_url_finders(config)

    assert result == {}


def test_get_only_links_from_html(tmp_path):
    """Test if we get only links from html files.
    We used app with css (app_links_css) and extra pages.
    Extra page is preserved.
    """
    builddir = tmp_path / 'build'

    with context_for_test('app_links_css') as module:
        freeze_config = {
            **module.freeze_config,
            'output': str(builddir),
            'url_finders': {'text/html': 'get_html_links'},
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'static' / 'OFL.txt').exists()
    assert (builddir / 'static' / 'style.css').exists()
    assert not (builddir / 'static' / 'TurretRoad-Regular.ttf').exists()


def test_get_only_links_from_css(tmp_path):
    """Test if we get only links from css files.
    We used app with css (app_links_css) and extra pages.
    Extra page is preserved.
    """
    builddir = tmp_path / 'build'

    with context_for_test('app_links_css') as module:
        freeze_config = {
            **module.freeze_config,
            'output': str(builddir),
            'url_finders': {'text/css': 'get_css_links'},
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'static' / 'OFL.txt').exists()
    assert not (builddir / 'static' / 'style.css').exists()
    assert not (builddir / 'static' / 'TurretRoad-Regular.ttf').exists()


def test_get_no_links(tmp_path):
    """Test configuration of no url_finders.
    We should get just root page.
    """
    builddir = tmp_path / 'build'

    with context_for_test('app_2pages') as module:
        freeze_config = {
            'output': str(builddir),
            'url_finders': {},
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert not (builddir / 'second_page.html').exists()


def test_get_only_links_from_self_made_url_finder(tmp_path):
    """Test if we freezer parse url_finder inserted as func type.
    """
    def my_url_finder(page_content, base_url, headers=None):
        return []


    builddir = tmp_path / 'build'

    with context_for_test('app_2pages') as module:
        freeze_config = {
            'output': str(builddir),
            'url_finders': {'text/html': my_url_finder},
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert not (builddir / 'second_page.html').exists()