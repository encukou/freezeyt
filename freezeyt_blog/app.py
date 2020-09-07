from flask import Flask, url_for, abort
from mistune import markdown
from pathlib import Path

app = Flask(__name__)

base_path = Path(__file__).parent

@app.route('/')
def index():
    """Start page with list of articles."""

    return f"""
    <html>
        <head>
            <title>Freezeyt blog</title>
        </head>
        <body>
            <h1>Vítejte na blogu o projektu freezeyt !</h1>
            <hr>
            <br>
            Všechny články k projektu:
            <br>
            <br>
            <a href={url_for('post', slug='lekce6')}>Článek o lekci 6</a>
            <br>
            <a href={url_for('post', slug='lekce7')}>Článek o lekci 7</a>
        </body>

    </html>
    """

@app.route('/<slug>')
def post(slug):
    md_file = base_path / f'content/articles/{slug}.md'
    try:
        file = open(md_file, mode='r', encoding='UTF-8')
    except FileNotFoundError:
        return abort(404)

    with file:
        md_content = file.read()

    html_content = markdown(md_content)

    return html_content





