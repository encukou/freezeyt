from flask import Flask, url_for

app = Flask(__name__)
freeze_config = {'prefix': 'http://čau-☺フ.даль.рф:8000/'}


@app.route('/')
def index():
    """Create the index page of the web app."""
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <a href="/čau/☺フ.html">Link 1</a>
            <a href="{url_for('page2')}">Link 2</a>
            <a href="http://čau-☺フ.даль.рф:8000/last_dance.html">Link 3</a>
            <a href='{url_for("page4", _external=True)}'>Link - external_True</a> to second page.
        </body>
    </html>
    """

@app.route('/čau/☺フ.html')
def page1():
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
    </html>
    """


@app.route('/☺フ/čau.html')
def page2():
    return """
    <html>
        <head>
            <title>Extra page 2</title>
        </head>
        <body>
            Page - 2
        </body>
    </html>
    """


@app.route('/last_dance.html')
def page3():
    return """
    <html>
        <head>
            <title>Extra page 3</title>
        </head>
        <body>
            Page - 3
        </body>
    </html>
    """

@app.route('/page4.html')
def page4():
    return """
    <html>
        <head>
            <title>Extra page 4</title>
        </head>
        <body>
            Page - 4
        </body>
    </html>
    """
