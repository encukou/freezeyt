from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def home():
    """Start page with list of articles."""

    return f"""
    <html>
        <head>
            <title>Vítejte na blogu o projektu freezeyt !</title>
        </head>
        <body>
            Seznam článků k projektu:
            <br>
            {url_for()}
            <a href='/second_page.html'>LINK</a> to second page.
        </body>

    </html>
    """

@app.route('/lesson6')
def lesson6():



