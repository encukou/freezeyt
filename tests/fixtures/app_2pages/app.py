from flask import Flask

app = Flask(__name__)

# For verification that this is the unchanged Flask app
app.is_the_fixture_app_2pages = True


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
            <a href='/second_page.html'>LINK</a> to second page.
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
            b"\n    <html>\n        <head>\n            <title>Hell"
            + b"o world</title>\n        </head>\n        <body>\n"
            + b"            Hello world!\n            <br>\n"
            + b"            <a href='/second_page.html'>LINK</a> t"
            + b"o second page.\n        </body>\n    </html>\n    ",

    'second_page.html':
            b"\n    <html>\n        <head>\n            <title>"
            + b"Hello world second page</title>\n        </head>\n"
            + b"        <body>\n            Second page !!!\n"
            + b"        </body>\n    </html>\n    "
}
