from flask import Flask, redirect, url_for, request
import pytest

from freezeyt import freeze, UnexpectedStatus, InfiniteRedirection

from testutil import raises_multierror_with_one_exception


FREEZEYT_CONFIGS = {
    'empty-config': {},
    'save': {'status_handlers': {'3xx': 'save'}},
    'follow': {'status_handlers': {'3xx': 'follow'}},
    'warn': {'status_handlers': {'3xx': 'warn'}},
}
@pytest.mark.parametrize("test_name", FREEZEYT_CONFIGS)
def test_redirect_to_same_frozen_file(test_name):
    """One URL redirects to next URL which freeze
    page to same filepath as would be freeyzed by first URL.
    """

    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to /index.html"""
        return redirect(url_for('index_html'))

    @app.route('/index.html')
    def index_html():
        return "Hello world!"

    config = {
        'output': {'type': 'dict'},
        **FREEZEYT_CONFIGS[test_name],
    }

    result = freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


def test_redirect_to_self():
    """Trivial redirect loop: the home page redirects to itself.

    This should result in UnexpectedStatus or InfiniteRedirection.
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to /index.html"""
        return redirect(url_for('index'))

    with raises_multierror_with_one_exception(UnexpectedStatus):
        config = {'output': {'type': 'dict'}}
        freeze(app, config)

    with raises_multierror_with_one_exception(InfiniteRedirection) as exc:
        config = {
            'output': {'type': 'dict'},
            'status_handlers': {'3xx': 'follow'},
        }
        freeze(app, config)

    assert "http://localhost:8000/" in str(exc.value)


def test_infinite_redirect_to_same_frozen_file():
    """Two different URLs redirect to same freezed file,
    then infinite loop is processing, so first URL redirect
    to latter and vice versa.
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to /index.html"""
        return redirect(url_for('index_html'))

    @app.route('/index.html')
    def index_html():
        """Redirecting to /"""
        return redirect(url_for('index'))

    with raises_multierror_with_one_exception(UnexpectedStatus):
        config = {'output': {'type': 'dict'}}
        freeze(app, config)

    with raises_multierror_with_one_exception(InfiniteRedirection) as exc:
        config = {
            'output': {'type': 'dict'},
            'status_handlers': {'3xx': 'follow'},
        }
        freeze(app, config)

    assert "http://localhost:8000/index.html" in str(exc.value)


@pytest.mark.parametrize("test_name", FREEZEYT_CONFIGS)
def test_redirect_to_same_frozen_file_with_double_hop(test_name):
    """Redirect via several pages that would all get saved to the same file.

    The final, non-redirecting page is the one that's saved.
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to //"""
        return redirect(url_for('index2'))

    @app.route('/index2')
    def index2():
        """Redirecting to /index.html"""
        return redirect(url_for('index_html'))

    @app.route('/index.html')
    def index_html():
        return "Hello world!"

    def always_index_html(url):
        return 'index.html'

    config = {
        'output': {'type': 'dict'},
        'url_to_path': always_index_html,
        **FREEZEYT_CONFIGS[test_name],
    }

    result = freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


def test_redirect_to_same_frozen_file_with_query_hop():
    """Add a redirect whose URL contains query parameter.
    Redirect URL with query parameter is prepared by
    first request of index page to app.

    The error here is not ideal, see:
    https://github.com/encukou/freezeyt/issues/401
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to /?query=cats"""
        if 'query' in request.args:
            return redirect(url_for('index_html'))
        else:
            return redirect(url_for('index', query="cats"))


    @app.route('/index.html')
    def index_html():
        assert not request.args
        return "Hello world!"

    with raises_multierror_with_one_exception(UnexpectedStatus):
        config = {'output': {'type': 'dict'}}
        freeze(app, config)

    with raises_multierror_with_one_exception(InfiniteRedirection):
        config = {
            'output': {'type': 'dict'},
            'status_handlers': {'3xx': 'follow'},
        }
        freeze(app, config)


def test_redirect_to_same_frozen_file_with_hop():
    """Add a new URL with no relation to index
    between URLs, which are freezed to same file.
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to /second_page.html"""
        return redirect(url_for('second_page'))

    @app.route('/second_page.html')
    def second_page():
        """Redirecting to /index.html"""
        return redirect(url_for('index_html'))

    @app.route('/index.html')
    def index_html():
        return "Hello world!"

    # By default, a redirect is considered an error.
    # The `/` -> `/second_page.html` is a normal redirect.
    with raises_multierror_with_one_exception(UnexpectedStatus):
        config = {'output': {'type': 'dict'}}
        freeze(app, config)

    # When following redirects, all of the pages have the same content.
    # But, we don't have the machinery to detect this yet,
    # so we raise an error.

    # TODO: This case should raise a better error.
    with raises_multierror_with_one_exception(InfiniteRedirection):
        config = {
            'output': {'type': 'dict'},
            'status_handlers': {'3xx': 'follow'},
        }
        freeze(app, config)


def test_redirect_with_same_path_with_different_spelling():
    """Check that the path of the file on disk is normalized when
    determining if URLs are saved to the same file
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        return redirect(url_for('index_html'))

    @app.route('/index.html')
    def index_html():
        return "Hello world!"

    def url_to_path(url):
        if url == '':
            return './index.html'
        elif url == 'index.html':
            return '././index.html'
        else:
            raise ValueError(f'unexpected URL path {url!r}')

    config = {
        'output': {'type': 'dict'},
        'url_to_path': url_to_path,
    }

    result = freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected
