from flask import Flask

wsgi_application = Flask(__name__)


@wsgi_application.route('/')
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

class SomeClass:
    def __init__(self):
        self.app = wsgi_application

obj = SomeClass()
