from flask import Flask, url_for, Response, request

app = Flask(__name__)


@app.route('/')
def index():
    """Create the index page of the web app."""
    return Response(f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <a href="/čau/☺フ">Link 1</a>
            <a href="{url_for('extra2')}">Link 2</a>
            <a href="/%E2%98%BA%E3%83%95/%8Dau">Link 3</a>
        </body>
    </html>
    """, content_type="text/html; charset=latin-1")

@app.route('/čau/☺フ')
def extra():
    print(request.environ)
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
    </html>
    """

@app.route('/☺フ/čau')
def extra2():
    print(request.environ)
    return """
    <html>
        <head>
            <title>Extra page 2</title>
        </head>
    </html>
    """
