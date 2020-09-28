from flask import Flask

app = Flask(__name__)


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
