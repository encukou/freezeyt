import imghdr
import mistune
from flask import Flask, url_for, abort, render_template, Response
from pathlib import Path
from urllib.parse import urlparse

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

BASE_PATH = Path(__file__).parent

ARTICLES_PATH = BASE_PATH / 'articles'
IMAGES_PATH = BASE_PATH / 'static/images'



class BlogRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            escaped = mistune.escape(code)
            return f'\n<pre><code>{escaped}</code></pre>\n'

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)

    def image(self, src, alt="", title=None):
        src = urlparse(src)
        if not src.netloc:
            filename = Path(src.path).name
            src = f"{ url_for('article_image', filename=filename) }"
            return f'\n<img src={src} alt={alt}>\n'

        return f'\n<img {mistune.escape(src, alt)} >\n'


@app.route('/')
def index():
    """Start page with list of articles."""
    post_names = [a.stem for a in sorted(ARTICLES_PATH.glob('*.md'))]

    return render_template(
        'index.html',
        post_names=post_names,
    )


@app.route('/<slug>/')
def post(slug):
    article = ARTICLES_PATH / f'{slug}.md'
    try:
        file = open(article, mode='r', encoding='UTF-8')
    except FileNotFoundError:
        return abort(404)

    with file:
        md_content = file.read()

    renderer = BlogRenderer()
    md = mistune.Markdown(renderer=renderer)
    html_content = md.render(md_content)

    return render_template(
        'post.html',
        content=html_content,
    )


@app.route('/article_image/<filename>')
def article_image(filename):
    """Route to returns images saved in static/images"""
    img_path = IMAGES_PATH / filename
    img_type = imghdr.what(img_path)
    if img_type:
        img_bytes = img_path.read_bytes()

        return Response(img_bytes, mimetype=f'image/{img_type}')

    return None
