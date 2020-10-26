from flask import Flask, url_for

app = Flask(__name__)


@app.route('/')
def index():
    """Create the index page of the web app."""
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <a href="/čau/☺フ">Link 1</a>
            <a href="{url_for('extra2')}">Link 2</a>
        </body>
    </html>
    """

@app.route('/čau/☺フ')
def extra():
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
    </html>
    """

@app.route('/☺フ/čau')
def extra2():
    return """
    <html>
        <head>
            <title>Extra page 2</title>
        </head>
    </html>
    """
