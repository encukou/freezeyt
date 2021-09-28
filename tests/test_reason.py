"""Test that the "reasons" attribute of UnexpectedStatus is set properly."""

import pytest

from flask import Flask, redirect

from freezeyt import freeze, UnexpectedStatus


def test_reason_homepage():
    app = Flask(__name__)
    config = {
        'prefix': 'http://localhost/',
        'output': {'type': 'dict'},
    }

    with pytest.raises(UnexpectedStatus) as e:
        freeze(app, config)
    assert str(e.value.url) == 'http://localhost:80/'
    assert e.value.status[:3] == '404'
    assert e.value.reasons == ['site root (homepage)']


def test_reason_redirect():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return redirect('http://localhost/404')

    config = {
        'prefix': 'http://localhost/',
        'output': {'type': 'dict'},
        'status_handlers': {'3xx': 'follow'},
    }

    with pytest.raises(UnexpectedStatus) as e:
        freeze(app, config)

    assert str(e.value.url) == 'http://localhost:80/404'
    assert e.value.status[:3] == '404'
    assert e.value.reasons == ['target of redirect from http://localhost:80/']


def test_reason_extra():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'OK'

    config = {
        'prefix': 'http://localhost/',
        'output': {'type': 'dict'},
        'extra_pages': ['404.html'],
    }

    with pytest.raises(UnexpectedStatus) as e:
        freeze(app, config)
    print(e)
    assert str(e.value.url) == 'http://localhost:80/404.html'
    assert e.value.status[:3] == '404'
    assert e.value.reasons == ['extra page']


def test_reason_link():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return '<a href="404.html">link to 404</a>'

    config = {
        'prefix': 'http://localhost/',
        'output': {'type': 'dict'},
    }

    with pytest.raises(UnexpectedStatus) as e:
        freeze(app, config)
    print(e)
    assert str(e.value.url) == 'http://localhost:80/404.html'
    assert e.value.status[:3] == '404'
    assert e.value.reasons == ['linked from http://localhost:80/']
