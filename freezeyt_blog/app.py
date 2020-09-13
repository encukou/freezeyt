import mistune
from flask import Flask, url_for, abort, render_template
from pathlib import Path

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

base_path = Path(__file__).parent
content_path = base_path / 'content/'

ARTICLES_PATH = content_path / 'articles/'
STATIC_PATH = content_path / 'images/'

class MyRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)


@app.route('/')
def index():
    """Start page with list of articles."""
    post_names = [a.stem for a in sorted(ARTICLES_PATH.glob('*.md'))]

    return render_template(
        'index.html',
        post_names=post_names,
    )


@app.route('/<slug>')
def post(slug):
    article = ARTICLES_PATH / f'{slug}.md'
    try:
        file = open(article, mode='r', encoding='UTF-8')
    except FileNotFoundError:
        return abort(404)

    with file:
        md_content = file.read()

    renderer = MyRenderer()
    md = mistune.Markdown(renderer=renderer)
    html_content = md.render(md_content)

    return render_template(
        'post.html',
        content=html_content,
    )





