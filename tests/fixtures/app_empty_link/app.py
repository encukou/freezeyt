from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    """Show index page of the web app.

    And link with empty URL, which we treat as a relative URL to the
    current page.
    No additional page is frozen, but we don't treat it as an error.
    """
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href=''>LINK</a> to this page.
        </body>
    </html>
    """


expected_dict = {
    'index.html':
            b"\n    <html>\n        <head>\n            <title>Hell"
            + b"o world</title>\n        </head>\n        <body>\n"
            + b"            Hello world!\n            <br>\n"
            + b"            <a href=''>LINK</a> t"
            + b"o this page.\n        </body>\n    </html>\n    ",
}
