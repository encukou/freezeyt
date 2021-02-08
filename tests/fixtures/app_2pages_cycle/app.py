from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    """Make index page.

    Link to the second page.
    Link to itself.
    """
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href='/second_page.html'>LINK</a> to second page.
            <br>
            <a href='/'>Return home</a>
        </body>
    </html>
    """


@app.route('/second_page.html')
def second_page():
    """Make the second page.

    Link back to the home page.
    """
    return """
    <html>
        <head>
            <title>Hello world second page</title>
        </head>
        <body>
            Second page!
            <a href='/'>Return home</a>
        </body>
    </html>
    """


expected_dict = {
    'index.html':
            b"\n    <html>\n        <head>\n            <title>Hell"
            + b"o world</title>\n        </head>\n        <body>\n"
            + b"            Hello world!\n            <br>\n"
            + b"            <a href='/second_page.html'>LINK</a> t"
            + b"o second page.\n            <br>\n"
            + b"            <a href='/'>Return home</a>\n"
            + b"        </body>\n    </html>\n    ",

    'second_page.html':
            b"\n    <html>\n        <head>\n            <title>"
            + b"Hello world second page</title>\n        </head>\n"
            + b"        <body>\n            Second page!\n"
            + b"            <a href='/'>Return home</a>\n"
            + b"        </body>\n    </html>\n    "
}