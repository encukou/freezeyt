from flask import Flask

app = Flask(__name__)
freeze_config = {'extra_pages': ['/extra/']}


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
}