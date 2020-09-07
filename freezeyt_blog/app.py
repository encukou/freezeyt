from flask import Flask, url_for, abort, render_template
from mistune import markdown
from pathlib import Path

app = Flask(__name__)

base_path = Path(__file__).parent

@app.route('/')
def index():
    """Start page with list of articles."""

    return render_template(
        'index.html',
        post_names=['lekce6', 'lekce7'],
    )


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





