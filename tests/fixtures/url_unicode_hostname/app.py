import sys

import pytest
from flask import Flask, url_for

app = Flask(__name__)
freeze_config = {'prefix': 'http://čau-☺フ.даль.рф:8000/'}
no_expected_directory = True


@app.route('/')
def index():
    """Create the index page of the web app."""
    if '8000-uye2a' in url_for("page4", _external=True):
        # On Python 3.6 & 3.7, the result of this url_for is
        # http://xn--au--eqa2078bpkn.xn--80ahw2e.xn--:8000-uye2a/page4.html
        # (with the *port* encoded).
        # If that's the case, let's skip the test.
        assert sys.version_info < (3, 8)
        pytest.skip('url_for() result has encoded port')
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <a href="/čau/☺フ.html">Link 1</a>
            <a href="{url_for('page2')}">Link 2</a>
            <a href="http://čau-☺フ.даль.рф:8000/last_dance.html">Link 3</a>
            <a href="{url_for("page4", _external=True)}">Link - external_True</a> to second page.
        </body>
    </html>
    """

@app.route('/čau/☺フ.html')
def page1():
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
    </html>
    """


@app.route('/☺フ/čau.html')
def page2():
    return """
    <html>
        <head>
            <title>Extra page 2</title>
        </head>
        <body>
            Page - 2
        </body>
    </html>
    """


@app.route('/last_dance.html')
def page3():
    return """
    <html>
        <head>
            <title>Extra page 3</title>
        </head>
        <body>
            Page - 3
        </body>
    </html>
    """

@app.route('/page4.html')
def page4():
    return """
    <html>
        <head>
            <title>Extra page 4</title>
        </head>
        <body>
            Page - 4
        </body>
    </html>
    """

expected_dict = {
    'index.html':
        b'\n    <html>\n        <head>\n            <title>Hello world</title>\n'
        + b'        </head>\n        <body>\n            '
        + '<a href="/čau/☺フ.html">Link 1</a>\n'.encode()
        + b'            '
        + b'<a href="/%E2%98%BA%E3%83%95/%C4%8Dau.html">Link 2</a>\n'
        + b'            '
        + '<a href="http://čau-☺フ.даль.рф:8000/last_dance.html">Link 3</a>\n'.encode()
        + b'            '
        + b'<a href="http://xn--au--eqa2078bpkn.xn--80ahw2e.xn--p1ai:8000/page4.html">Link - external_True</a> to second page.\n'
        + b'        </body>\n    </html>\n    ',

    'last_dance.html':
        b'\n    <html>\n        <head>\n            <title>Extra '
        + b'page 3</title>\n        </head>\n        <body>\n      '
        + b'      Page - 3\n        </body>\n    </html>\n    ',

    'page4.html':
        b'\n    <html>\n        <head>\n            <title>Extra page'
        + b' 4</title>\n        </head>\n        <body>\n            Pa'
        + b'ge - 4\n        </body>\n    </html>\n    ',

    'čau': {
        '☺フ.html':
            b'\n    <html>\n        <head>\n            <title>Extra '
            + b'page</title>\n        </head>\n    </html>\n    '
        },

    '☺フ': {
        'čau.html':
            b'\n    <html>\n        <head>\n            <title>Extra '
            + b'page 2</title>\n        </head>\n        <body>\n      '
            + b'      Page - 2\n        </body>\n    </html>\n    '
        },

}
