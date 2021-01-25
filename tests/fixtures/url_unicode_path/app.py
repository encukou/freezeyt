from flask import Flask, url_for, Response

app = Flask(__name__)
freeze_config = {'extra_pages': ['/éxtrą/']}
no_expected_directory = True


@app.route('/')
def index():
    """Create the index page of the web app."""
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <a href="/čau/☺フ.html">Link 1</a>
            <a href="{url_for('extra2')}">Link 2</a>
        </body>
    </html>
    """

@app.route('/čau/☺フ.html')
def extra():
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
    </html>
    """

@app.route('/☺フ/čau.html')
def extra2():
    return Response(b"""
    <html>
        <head>
            <title>Extra page 2</title>
        </head>
        <body>
            <a href="/constant/\xf0.html">Link</a>
        </body>
    </html>
    """, content_type='text/html; charset=cp1253')

@app.route('/constant/π.html')
def extra_pi():
    return """
    <html>
        <head>
            <title>Extra page Pi</title>
        </head>
    </html>
    """

@app.route('/éxtrą/')
def extra_page():
    return """
    <html>
        <head>
            <title>éxtrą page</title>
        </head>
    </html>
    """


expected_dict = {
    'constant': {
        'π.html':
            b'\n    <html>\n        <head>\n            <title>Ex'
            + b'tra page Pi</title>\n        </head>\n    </html>\n    '
    },
    'index.html': 
        b'\n    <html>\n        <head>\n            <title>Hello worl'
        + b'd</title>\n        </head>\n        <body>\n            <a '
        + b'href="/\xc4\x8dau/\xe2\x98\xba\xe3\x83\x95.html">Link 1</a>\n'
        + b'            <a href="/%E2%98%BA%E3%83%95/%C4%8Dau.html">Link'
        + b' 2</a>\n        </body>\n    </html>\n    ',
    'éxtrą': {
        'index.html':
            b'\n    <html>\n        <head>\n            <titl'
            + b'e>\xc3\xa9xtr\xc4\x85 page</title>\n        </hea'
            + b'd>\n    </html>\n    '
        },
    'čau': {
        '☺フ.html':
            b'\n    <html>\n        <head>\n            <title>Extra '
            + b'page</title>\n        </head>\n    </html>\n    '
    },
    '☺フ': {
        'čau.html':
            b'\n    <html>\n        <head>\n            <title>Extra '
            + b'page 2</title>\n        </head>\n        <body>\n      '
            + b'      <a href="/constant/\xf0.html">Link</a>\n        </'
            + b'body>\n    </html>\n    '
    }
}
