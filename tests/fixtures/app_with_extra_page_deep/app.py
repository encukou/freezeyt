from flask import Flask

app = Flask(__name__)
freeze_config = {'extra_pages': ['/extra/', '/extra/extra_deep/']}


@app.route('/')
def index():
    """Create the index page of the web app."""
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """

@app.route('/extra/')
def extra():
    return """
    <html>
        <head>
            <title>Extra page</title>
        </head>
        <body>
            This is unreachable via links.
        </body>
    </html>
    """


@app.route('/extra/extra_deep/')
def extra_deep():
    return """
    <html>
        <head>
            <title>Extra DEEP page</title>
        </head>
        <body>
            This is unreachable via links.
            <strong>Extra Deep page</strong>
        </body>
    </html>
    """
