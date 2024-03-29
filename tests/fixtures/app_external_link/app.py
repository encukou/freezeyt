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
            <br>
            <a href='https://naucse.python.cz'>LINK</a> to external page.
            <a href='mailto:someone@domain.test'>LINK</a> to an e-mail address.
        </body>
    </html>
    """


expected_dict = {
    'index.html':
            b"\n    <html>\n        <head>\n"
            + b"            <title>Hello world</title>\n"
            + b"        </head>\n        <body>\n            Hello world!\n"
            + b"            <br>\n            "
            + b"<a href='https://naucse.python.cz'>LINK</a> to external page.\n"
            + b"            <a href='mailto:someone@domain.test'>LINK</a> to an e-mail address.\n"
            + b"        </body>\n    </html>\n    "
}
