from flask import Flask, redirect, url_for

from freezeyt import freeze

def test_redirect_to_itself_by_different_URL():
    """WSGI app can define for one static file
    different URLs with different content (e.g. '/', '/index.html'),
    It is complicated for Freezeyt as static server to disntict
    two different URLs for one static file.
    One content will be always lost.
    In case of redirection ..... ????????
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

    result=freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


def test_infinite_redirect_to_itself_by_different_URL():
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


def test_redirect_to_itself_by_different_URL_with_double_slash_hop():
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

    result=freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


def test_redirect_to_itself_by_different_URL_with_query_hop():
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Redirecting to /?query=cats"""
        return redirect(url_for('index_query'))

    @app.route('/?query=cats')
    def index_query():
        """Redirecting to /index.html"""
        return redirect(url_for('index_html'))

    @app.route('/index.html')
    def index_html():
        return "Hello world!"

    config = {
        'output': {'type': 'dict'},
    }

    result=freeze(app, config)

    expected = {'index.html': b"Hello world!"}

    assert result == expected


def test_redirect_to_itself_by_different_URL_with_hop():
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

    result=freeze(app, config)

    expected = {
        'index.html': b"Hello world!",
        'second_page.html': b"Hello world!",
    }

    assert result == expected

