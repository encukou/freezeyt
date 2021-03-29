import mimetypes
import mistune
from flask import Flask, url_for, abort, render_template, Response
from pathlib import Path
from urllib.parse import urlparse
import html

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

    def image(self, src, title, alt_text):
        src_parse = urlparse(src)
        alt_text = html.escape(alt_text, quote=True)

        if title:
            title_part = f'title="{html.escape(title, quote=True)}"'
        else:
            title_part = ""

        if not src_parse.netloc:
            filename = Path(src_parse.path).name
            src = url_for('article_image', filename=filename)
            src = html.escape(src, quote=True)
            return f'\n<img src="{src}" alt="{alt_text}" {title_part}>\n'

        src = html.escape(src, quote=True)
        return f'\n<img src="{src}" alt="{alt_text}" {title_part}>\n'


@app.route('/')
def index():
    """Start page with list of articles."""
    post_slugs = [a.stem for a in sorted(ARTICLES_PATH.glob('*.md'))]
    post_names = []
    for article in sorted(ARTICLES_PATH.glob('*.md')):
        with open(article, encoding='utf-8') as a:
            post_names.append(a.readline()[2:])
    post_info = zip(post_slugs, post_names)

    return render_template(
        'index.html',
        post_info=post_info
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
    (mimetype, encoding) = mimetypes.guess_type(img_path)
    if mimetype:
        img_bytes = img_path.read_bytes()
        print(mimetype)

        return Response(img_bytes, mimetype=mimetype)

    return None
