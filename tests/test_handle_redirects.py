from flask import Flask, redirect, url_for, request
import pytest

from freezeyt import freeze, UnexpectedStatus, InfiniteRedirection

from testutil import raises_multierror_with_one_exception


def test_redirect_to_same_frozen_file():
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

    config = {'output': {'type': 'dict'}}

    result = freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


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

    # TODO: This should raise a MultiError.
    with pytest.raises(InfiniteRedirection):
        config = {
            'output': {'type': 'dict'},
            'status_handlers': {'3xx': 'follow'},
        }
        freeze(app, config)


def test_redirect_to_same_frozen_file_with_double_slash_hop():
    """Add to redirecting tracerout a node with double slash URL.
    Finally, the double slash URL redirects to page where is some
    content.
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to //"""
        return redirect(url_for('index_double_slash'))

    @app.route('//')
    def index_double_slash():
        """Redirecting to /index.html"""
        return redirect(url_for('index_html'))

    @app.route('/index.html')
    def index_html():
        return "Hello world!"

    config = {
        'output': {'type': 'dict'},
    }

    result = freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


def test_redirect_to_same_frozen_file_with_query_hop():
    """Add a redirect whose URL contains query parameter.
    Redirect URL with query parameter is prepared by
    first request of index page to app.
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

    config = {
        'output': {'type': 'dict'},
    }

    result = freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


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
        config = {
            'output': {'type': 'dict'},
        }
        freeze(app, config)

    # When following redirects, all of the pages have the same content.
    # But, we don't have the machinery to detect this yet,
    # so we raise an error.

    # TODO: This should raise a MultiError.
    # TODO: This case should raise a better error.
    with pytest.raises(InfiniteRedirection):
        config = {
            'output': {'type': 'dict'},
            'status_handlers': {'3xx': 'follow'},
        }
        freeze(app, config)

