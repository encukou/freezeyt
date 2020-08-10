from flask import Flask, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <img src='{url_for("static", filename="smile.png")}'>
        </body>
    </html>
    """
