from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href='/second_page.html'>LINK</a> to second page.
        </body>
    </html>
    """


@app.route('/second_page.html')
def second_page():
    return """
    <html>
        <head>
            <title>Hello world second page</title>
        </head>
        <body>
            Second page !!!
            <a href='/third_page.html'>LINK</a> to page 3.
        </body>
    </html>
    """


@app.route('/third_page.html')
def third_page():
    return """
    <html>
        <head>
            <title>Hello world third page</title>
        </head>
        <body>
            Page 3 !!!
        </body>
    </html>
    """
