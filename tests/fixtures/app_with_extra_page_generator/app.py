from flask import Flask

app = Flask(__name__)
freeze_config = {'extra_pages': [{'generator': 'app:generate_extra_pages'}]}


def generate_extra_pages(app):
    yield 'extra/'
    yield 'extra2/'


@app.route('/')
def index():
    """Create the index page of the web app."""
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """

@app.route('/extra/')
def extra():
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
        <body>
            This is unreachable via links.
        </body>
    </html>
    """

@app.route('/extra2/')
def extra2():
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
        <body>
            This is also unreachable via links.
        </body>
    </html>
    """


expected_dict = {
    'index.html':
        b'\n    <html>\n        <head>\n            <title>Hell'
        + b'o world</title>\n        </head>\n        <body>\n'
        + b'            Hello world!\n        </body>\n    </html>\n    ',

    'extra': {
        'index.html':
            b"\n    <html>\n        <head>\n"
            + b"            <title>Extra page</title>\n        </head>\n"
            + b"        <body>\n            This is unreachable via links.\n"
            + b"        </body>\n    </html>\n    "
    },

    'extra2': {
        'index.html':
            b"\n    <html>\n        <head>\n"
            + b"            <title>Extra page</title>\n        </head>\n"
            + b"        <body>\n            This is also unreachable via links.\n"
            + b"        </body>\n    </html>\n    "
    },
}
