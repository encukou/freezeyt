from pathlib import Path

from flask import Flask, Response

app = Flask(__name__)


@app.route('/')
def index():
    """Create the index page of the web app."""
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <img src="/image.jpg">
            <a href="/second_page.HTML"
        </body>
    </html>
    """

@app.route('/image.jpg')
def image():
    img_path = Path(__file__).parent / 'smile.png'
    img_bytes = img_path.read_bytes()
    return Response(img_bytes, mimetype='image/png')

@app.route('/capital_extension.HTML')
def second_page():
    return """
    <html>
        <head>
            <title>Second page</title>
        </head>
        <body>
            Second page!
        </body>
    </html>
    """
