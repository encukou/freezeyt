from flask import Flask, url_for

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!<br>
            <a href="/about">About page</a>
        </body>
    </html>
    """


@app.route("/about")
def about():
    return """
    <html>
        <head>
            <title>About</title>
        </head>
        <body>
            <h2>We are czech community of PyLadies !!!</h2>
        </body>
    </html>
    """

