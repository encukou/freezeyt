from flask import Flask, url_for, Response
app = Flask(__name__)
extra_pages = ['/éxtrą/']


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
