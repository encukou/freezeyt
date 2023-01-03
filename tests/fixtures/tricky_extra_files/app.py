from pathlib import Path

from flask import Flask

APP_DIR = Path(__file__).parent

app = Flask(__name__)


freeze_config = {
    'extra_files': {'static': {'copy_from': str(APP_DIR / 'static_dir')}},
}


@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <a href='/static/file.txt'>text file</a>
            <a href='/static-not.html'>Trick page</a>
        </body>
    </html>
    """

@app.route('/static-not.html')
def trick_page():
    """This should not be looked up in static_dir."""
    return "<html>...</html>"

@app.route('/static/missing.html')
def should_be_missing():
    """This should be looked up in static_dir.
    This function should be ignored.
    """
    return "<html>...</html>"


expected_dict = {
    'index.html': b"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <a href='/static/file.txt'>text file</a>
            <a href='/static-not.html'>Trick page</a>
        </body>
    </html>
    """,
    'static-not.html': b'<html>...</html>',
    'static': {
        'file.txt': b'Hello\n',

    },
}
