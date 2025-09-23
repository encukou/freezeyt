import asyncio
from typing import Dict, Tuple, Callable

import pytest
from flask import Flask

from freezeyt import freeze
from freezeyt.freezer import parse_handlers as parse_url_finders
from freezeyt.url_finders import get_html_links
from freezeyt.url_finders import get_css_links
from testutil import context_for_test
from testutil import raises_multierror_with_one_exception


TEST_DATA: Dict[str, Tuple[str, Dict[str, str], Callable]] = {
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

    result: Dict[str, Callable] = parse_url_finders(
        config, default_module='freezeyt.url_finders')
    assert result[key] == expected


def test_get_no_url_finders():
    url_finders: dict = {}

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

        freeze_config['extra_pages'] += ["static/style.css"]
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


def test_get_no_links_by_none(tmp_path):
    """Test configuration of all url_finders set to 'none'.
    We should get just root page.
    """
    builddir = tmp_path / 'build'

    with context_for_test('app_links_css') as module:
        freeze_config = {
            'output': str(builddir),
            'url_finders': {
                'text/html': 'none',
                'text/css': 'none',
            },
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
    return ['third_page.html']

async def url_finder_async(page_content, base_url, headers=None):
    return ['third_page.html']

def url_generator_sync(page_content, base_url, headers=None):
    yield 'third_page.html'

async def url_generator_async(page_content, base_url, headers=None):
    await asyncio.sleep(0)
    yield 'third_page.html'
    await asyncio.sleep(0)

@pytest.mark.parametrize('name', (
    'url_finder_sync', 'url_finder_async',
    'url_generator_sync', 'url_generator_async',
))
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
    assert (builddir / 'third_page.html').exists()


@pytest.mark.parametrize('name', (
    'url_finder_sync', 'url_finder_async',
    'url_generator_sync', 'url_generator_async',
))
def test_get_url_finder_by_name_from_header(name):
    """Test if we freezer honors the Freezeyt-URL-Finder header.
    """

    app = Flask(__name__)

    @app.route('/')
    def index():
        return (
            '<a href="ignored_page_1.html">...</a>',
            {'Freezeyt-URL-Finder': f'{__name__}:{name}'},
        )

    @app.route('/third_page.html')
    def visited():
        return '<a href="ignored_page_2.html">...</a>'

    freeze_config = {
        'output': {'type': 'dict'},
        'url_finders': {'text/html': 'none'},
    }

    result = freeze(app, freeze_config)

    assert result == {
        'index.html': b'<a href="ignored_page_1.html">...</a>',
        'third_page.html': b'<a href="ignored_page_2.html">...</a>',
    }


def test_builtin_url_finder_by_name():
    """Test if we freezer honors the Freezeyt-URL-Finder header.
    """

    app = Flask(__name__)

    @app.route('/')
    def index():
        return """
            <a href="html_links.html">...</a>
            <a href="css_links.html">...</a>
            <a href="none.html">...</a>
        """

    @app.route('/html_links.html')
    def html_links():
        return (
            '''
                <a href="found_html.html">...</a>
                * { background-image: url(notfound_css.html); }
            ''',
            {'Freezeyt-URL-Finder': 'get_html_links'},
        )

    @app.route('/css_links.html')
    def css_links():
        return (
            '''
                /* <a href="notfound_css.html">...</a> */
                * { background-image: url(found_css.html); }
            ''',
            {'Freezeyt-URL-Finder': 'get_css_links'},
        )

    @app.route('/none.html')
    def none_links():
        return (
            '''
                /* <a href="notfound_none.html">...</a> */
                * { background-image: url(notfound_none.html); }
            ''',
            {'Freezeyt-URL-Finder': 'none'},
        )

    @app.route('/found_html.html')
    def found_html():
        return 'OK'

    @app.route('/found_css.html')
    def found_css():
        return 'OK'

    freeze_config = {
        'output': {'type': 'dict'},
    }

    result = freeze(app, freeze_config)

    assert set(result) == {
       'index.html',
       'html_links.html',
       'css_links.html',
       'none.html',
       'found_css.html',
       'found_html.html',
    }


def test_get_url_from_link_header():
    app = Flask(__name__)
    @app.route('/')
    def index():
        return (
            'index',
            [
                ('Link', '<page_a.html>; rel="preload", <page_b.html>; rel="alternate prerender"; crossorigin="anonymous"'),
                ('Link', '<https://localhost/page_c.html>; rel="preload"'),
            ],
        )

    @app.route('/page_<n>.html')
    def page(n):
        return f'page {n}'

    freeze_config = {
        'output': {'type': 'dict'},
        'prefix': 'https://localhost/',
    }

    result = freeze(app, freeze_config)

    assert result == {
        'index.html': b'index',
        'page_a.html': b'page a',
        'page_b.html': b'page b',
        'page_c.html': b'page c',
    }


@pytest.mark.parametrize('link', (
    'Bad link.',
    '<bad/link',
    'bad1, bad2',
    '<https://good.example/>, <bad',
    '<https://good.example/>; foo, bad',
))
def test_bad_link_header(link):
    app = Flask(__name__)
    @app.route('/')
    def index():
        return (
            'index',
            [
                ('Link', link),
            ],
        )

    freeze_config = {
        'output': {'type': 'dict'},
        'prefix': 'https://localhost/',
    }

    with raises_multierror_with_one_exception(ValueError):
        freeze(app, freeze_config)


@pytest.mark.parametrize('link', (
    '<https://localhost/page_c.html>; rel="preload"',
    'Bad link.',
))
def test_link_header_disabled(link):
    app = Flask(__name__)
    @app.route('/')
    def index():
        return (
            '<a href="second.html">...</a>',
            [
                ('Link', link),
            ],
        )

    @app.route('/second.html')
    def second():
        return 'second'

    freeze_config = {
        'output': {'type': 'dict'},
        'prefix': 'https://localhost/',
        'urls_from_link_headers': False,
    }

    result = freeze(app, freeze_config)

    assert result == {
        'index.html': b'<a href="second.html">...</a>',
        'second.html': b'second',
    }
