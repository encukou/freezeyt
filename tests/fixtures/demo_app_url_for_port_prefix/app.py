from flask import Flask, url_for

app = Flask(__name__)
prefix = 'http://freezeyt.test:1234/foo/'


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

