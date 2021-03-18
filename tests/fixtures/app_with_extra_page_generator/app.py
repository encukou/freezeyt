from flask import Flask

def generate_extra_pages_0(app):
    yield 'extra/'
    yield 'extra2/'

def generate_extra_pages_1(app):
    yield 'extra3/'
    yield 'extra4/'

def generate_extra_pages_2(app):
    yield 'extra5/'
    yield 'extra6/'

app = Flask(__name__)
freeze_config = {
    'extra_pages': [
        {'generator': 'app:generate_extra_pages_0'},
        {'generator': generate_extra_pages_1},
        generate_extra_pages_2,
    ]
}
config_is_serializable = False


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

@app.route('/extra<int:number>/')
def extra2(number):
    return f"""Extra page {number}"""


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

    'extra2': {'index.html': b'Extra page 2'},
    'extra3': {'index.html': b'Extra page 3'},
    'extra4': {'index.html': b'Extra page 4'},
    'extra5': {'index.html': b'Extra page 5'},
    'extra6': {'index.html': b'Extra page 6'},
}
