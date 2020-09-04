from flask import Flask, url_for, render_template
from mistune import markdown
from pathlib import Path

app = Flask(__name__)

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
            <a href={url_for('lesson6')}>Článek o lekci 6</a>
            <br>
            <a href={url_for('lesson7')}>Článek o lekci 7</a>
        </body>

    </html>
    """

@app.route('/lekce6')
def lesson6():
    md_file = Path('content/articles/lekce6.md')
    with open(md_file, mode='r', encoding='UTF-8') as f:
        md_content = f.read()

    html_content = markdown(md_content)

    return html_content

@app.route('/lekce7')
def lesson7():
    md_file = Path('content/articles/lekce7.md')
    with open(md_file, mode='r', encoding='UTF-8') as f:
        md_content = f.read()

    html_content = markdown(md_content)

    return html_content





