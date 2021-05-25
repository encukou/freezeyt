from flask import Flask, url_for, Response

app = Flask(__name__)
freeze_config = {'default_mimetype': 'text/plain'}


@app.route('/')
def index():
    """Create the index page of the web app."""
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <a href="{url_for('textfile')}">Link</a>
        </body>
    </html>
    """

@app.route('/textfile')
def textfile():
    return Response("Hello", mimetype='text/plain')


expected_dict = {
    'index.html':
        b'\n    <html>\n        <head>\n            <title>Hello world</title>'
        + b'\n        </head>\n        <body>\n            '
        + b'<a href="/textfile">Link</a>\n        </body>\n    </html>\n    ',
    'textfile': b'Hello',
}
