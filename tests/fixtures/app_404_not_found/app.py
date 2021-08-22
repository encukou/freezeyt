from flask import Flask

app = Flask(__name__)
freeze_config = {'ignore_404_not_found': True}

@app.route('/')
def index():
    """Show index page of the web app.

    And link to the second page.
    """
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href='/not_found.html'>LINK</a> to second page.
        </body>
    </html>
    """

expected_dict = {
    'index.html':
            b"\n    <html>\n        <head>\n            <title>Hell"
            + b"o world</title>\n        </head>\n        <body>\n"
            + b"            Hello world!\n            <br>\n"
            + b"            <a href='/not_found.html'>LINK</a> t"
            + b"o second page.\n        </body>\n    </html>\n    ",

    'not_found.html':
            b"\n    <html>\n        <head>\n            <title>404"
            + b"not found</title>\n        </head>\n        <body>\n"
            + b"            404 - Page not found\n"
            + b"        </body>\n    </html>\n    ",
}