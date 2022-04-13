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
        </body>
    </html>
    """

@app.route('/image.jpg')
def image():
    img_path = Path(__file__).parent / 'smile.png'
    img_bytes = img_path.read_bytes()
    return Response(img_bytes, mimetype='image/png')
