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
        </body>
    </html>
    """


expected_dict = {
    'index.html':
            b'\n    <html>\n        <head>\n'
            + b'            <title>Hello world</title>\n        </head>\n'
            + b'        <body>\n            Hello world!\n'
            + b'            <a href="nowhere">Link to nowhere</a>\n'
            + b'        </body>\n    </html>\n    '

}