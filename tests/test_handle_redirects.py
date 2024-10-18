from flask import Flask, redirect, url_for, request

from freezeyt import freeze

def test_redirect_to_same_static_file():
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


def test_infinite_redirect_to_same_static_file():
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

    config = {'output': {'type': 'dict'}}

    freeze(app, config)


def test_redirect_to_same_static_file_with_double_slash_hop():
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


def test_redirect_to_same_static_file_with_query_hop():
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


def test_redirect_to_same_static_file_with_hop():
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

    config = {
        'output': {'type': 'dict'},
    }

    result = freeze(app, config)

    expected = {
        'index.html': b"Hello world!",
        'second_page.html': b"Hello world!",
    }

    assert result == expected

