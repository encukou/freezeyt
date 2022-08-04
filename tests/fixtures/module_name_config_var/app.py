from flask import Flask

config_is_serializable = False

app = Flask(__name__)

freeze_config = {'app': __name__}

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

expected_dict = {
    'index.html':
        b'\n    <html>\n        <head>\n            <title>Hell'
        + b'o world</title>\n        </head>\n        <body>\n'
        + b'            Hello world!\n        </body>\n    </html>\n    '
}