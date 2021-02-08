from flask import Flask, url_for

app = Flask(__name__)
freeze_config = {'prefix': 'http://freezeyt.test/foo/'}

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
            <a href='{url_for("third_page")}'>external_False</a> to third page.
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


@app.route('/third_page.html')
def third_page():
    """Show the third page."""
    return """
    <html>
        <head>
            <title>Hello world third page</title>
        </head>
        <body>
            Third page !!!
        </body>
    </html>
    """


expected_dict = {
    'index.html':
        b"\n    <html>\n        <head>\n            "
        + b"<title>Hello world</title>\n        </head>\n"
        + b"        <body>\n            Hello world!\n"
        + b"            <br>\n            <a href='http://freezeyt.te"
        + b"st/foo/second_page.html'>external_True</a> to second page.\n"
        + b"            <a href='/foo/third_page.html'>external_False</a> to "
        + b"third page.\n        </body>\n    </html>\n    ",

    'second_page.html':
        b"\n    <html>\n        <head>\n"
        + b"            <title>Hello world second page</title>\n"
        + b"        </head>\n        <body>\n            Second page !!!\n"
        + b"        </body>\n    </html>\n    ",

    'third_page.html':
        b"\n    <html>\n        <head>\n"
        + b"            <title>Hello world third page</title>\n"
        + b"        </head>\n        <body>\n            Third page !!!\n"
        + b"        </body>\n    </html>\n    ",

}