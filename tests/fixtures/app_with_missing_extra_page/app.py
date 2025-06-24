from flask import Flask

app = Flask(__name__)
freeze_config = {'extra_pages': ['extra/']}


@app.route('/')
def index():
    """Create the index page of the web app."""
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """
