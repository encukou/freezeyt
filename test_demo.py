import pytest
from demo_app import app

from freezeyt import freeze

def test_one_page():
    freeze(app, "/tmp/frozen")

    with open("/tmp/frozen/index.html", encoding='utf-8') as f:
        read_text = f.read()

    assert read_text == """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """
