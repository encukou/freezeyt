import pytest

from freezeyt import freeze
from freezeyt.freezer import parse_handlers as parse_url_finders
from freezeyt.url_finders import get_html_links
from freezeyt.url_finders import get_css_links
from testutil import context_for_test


TEST_DATA = {
    'html_links_fallback':
        (   'text/html',
            {'text/html': 'get_html_links'},
            (get_html_links)
        ),
    'css_links_fallback':
        (   'text/css',
            {'text/css': 'get_css_links'},
            (get_css_links)
        ),
}


@pytest.mark.parametrize("test_name", TEST_DATA)
def test_parse_url_finders(test_name):
    key, config, expected = TEST_DATA[test_name]

    assert parse_url_finders(
        config, default_module='freezeyt.url_finders')[key] == expected


def test_get_no_url_finders():
    url_finders = {}

    assert parse_url_finders(
        url_finders, default_module='freezeyt.url_finders') == {}


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
            'use_default_url_finders': False,
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'second_page.html').exists()
    assert (builddir / 'static' / 'OFL.txt').exists()
    assert (builddir / 'static' / 'style.css').exists()
    assert not (builddir / 'static' / 'TurretRoad-Regular.ttf').exists()


def test_only_html_links_keep_css_default(tmp_path):
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
    assert (builddir / 'second_page.html').exists()
    assert (builddir / 'static' / 'OFL.txt').exists()
    assert (builddir / 'static' / 'style.css').exists()
    assert (builddir / 'static' / 'TurretRoad-Regular.ttf').exists()

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
            'use_default_url_finders': False,
        }

        freeze_config['extra_pages'] += ["/static/style.css"]
        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert not (builddir / 'second_page.html').exists()
    assert (builddir / 'static' / 'OFL.txt').exists()
    assert (builddir / 'static' / 'style.css').exists()
    assert (builddir / 'static' / 'TurretRoad-Regular.ttf').exists()


def test_get_no_links(tmp_path):
    """Test configuration of no url_finders.
    We should get just root page.
    """
    builddir = tmp_path / 'build'

    with context_for_test('app_links_css') as module:
        freeze_config = {
            'output': str(builddir),
            'use_default_url_finders': False,
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert not (builddir / 'second_page.html').exists()
    assert not (builddir / 'static' / 'OFL.txt').exists()
    assert not (builddir / 'static' / 'style.css').exists()
    assert not (builddir / 'static' / 'TurretRoad-Regular.ttf').exists()


@pytest.mark.parametrize('found_url', (
    'http://localhost:8000/third_page.html',
    '/third_page.html',
    'third_page.html',
))
@pytest.mark.parametrize('use_async', (True, False))
def test_get_url_finder_callable_defined_by_user(found_url, tmp_path, use_async):
    """Test if we freezer parse url_finder inserted as func type by user.
    """
    def sync_url_finder(page_content, base_url, headers=None):
        return [found_url]

    async def async_url_finder(page_content, base_url, headers=None):
        return [found_url]

    if use_async:
        my_url_finder = async_url_finder
    else:
        my_url_finder = sync_url_finder

    builddir = tmp_path / 'build'

    with context_for_test('app_3pages_deep') as module:
        freeze_config = {
            'output': str(builddir),
            'url_finders': {'text/html': my_url_finder},
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert not (builddir / 'second_page.html').exists()
    assert (builddir / 'third_page.html').exists()


def url_finder_sync(page_content, base_url, headers=None):
    return []

async def url_finder_async(page_content, base_url, headers=None):
    return []

@pytest.mark.parametrize('name', ('url_finder_sync', 'url_finder_async'))
def test_get_url_finder_by_name_defined_by_user(tmp_path, name):
    """Test if we freezer parse url_finder inserted as func type.
    """

    builddir = tmp_path / 'build'

    with context_for_test('app_3pages_deep') as module:
        freeze_config = {
            'output': str(builddir),
            'url_finders': {'text/html': f'{__name__}:{name}'},
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert not (builddir / 'second_page.html').exists()
    assert not (builddir / 'third_page.html').exists()
