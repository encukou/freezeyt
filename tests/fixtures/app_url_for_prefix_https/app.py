from flask import Flask, url_for

app = Flask(__name__)
freeze_config = {'prefix': 'https://freezeyt.test/foo/'}

@app.route('/')
def index():
    """Show index page of the web app.

    And link to the second page.
    """
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href='{url_for("second_page", _external=True)}'>external_True</a> to second page.
        </body>
    </html>
    """


@app.route('/second_page.html')
def second_page():
    """Show the second page."""
    return """
    <html>
        <head>
            <title>Hello world second page</title>
        </head>
        <body>
            Second page !!!
        </body>
    </html>
    """


expected_dict = {
    'index.html':
        b"\n    <html>\n        <head>\n            "
        + b"<title>Hello world</title>\n        </head>\n"
        + b"        <body>\n            Hello world!\n"
        + b"            <br>\n            <a href='https://freezeyt.te"
        + b"st/foo/second_page.html'>external_True</a> to second page.\n"
        + b"        </body>\n    </html>\n    ",

    'second_page.html':
        b"\n    <html>\n        <head>\n"
        + b"            <title>Hello world second page</title>\n"
        + b"        </head>\n        <body>\n            Second page !!!\n"
        + b"        </body>\n    </html>\n    ",

}
