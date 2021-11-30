from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <a href="nowhere">Link to nowhere</a>
            <a href="also_nowhere">Link to nowhere</a>
        </body>
    </html>
    """
