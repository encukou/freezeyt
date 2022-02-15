import mimetypes
from markdown_it import MarkdownIt
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


def highlighter(code, lang_name, lang_attrs):
    if not lang_name:
        return html.escape(code)

    lexer = get_lexer_by_name(lang_name, stripall=True)
    formatter = HtmlFormatter(nowrap=True)
    return highlight(code, lexer, formatter)


def render_img(self, tokens, idx, options, env):
    [token] = tokens

    src = token.attrs['src']
    alt_text = token.content
    title = token.attrs.get('title')

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
    articles = sorted(ARTICLES_PATH.glob('*.md'))
    post_info = []

    for article in articles:
        with open(article, encoding='utf-8') as a:
            title = a.readline()
            if not title.startswith("# "):
                raise ValueError("Post must begin with a title.")

        slug = article.stem
        title = title.lstrip("# ").strip()
        post_info.append((slug, title))

    return render_template('index.html', post_info=post_info)


@app.route('/<slug>/')
def post(slug):
    article = ARTICLES_PATH / f'{slug}.md'
    try:
        file = open(article, mode='r', encoding='UTF-8')
    except FileNotFoundError:
        return abort(404)

    with file:
        md_content = file.read()

    renderer = MarkdownIt("commonmark", {"highlight": highlighter})
    renderer.add_render_rule("image", render_img)
    html_content = renderer.render(md_content)

    return render_template('post.html', content=html_content)


@app.route('/article_image/<filename>')
def article_image(filename):
    """Route to returns images saved in static/images"""
    img_path = IMAGES_PATH / filename
    (mimetype, encoding) = mimetypes.guess_type(filename)
    if mimetype:
        img_bytes = img_path.read_bytes()

        return Response(img_bytes, mimetype=mimetype)

    return None
