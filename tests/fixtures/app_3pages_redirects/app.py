from flask import Flask, Response, url_for

app = Flask(__name__)
freeze_config = {
    'status_handlers': {'3xx': 'follow'},
}

@app.route('/')
def index():
    """Redirect to the second page.
    """
    return Response(
        "Redirecting to second page...",
        status='301 Moved Permanently',
        headers=[('Location', url_for('second_page'))],
    )


@app.route('/second_page.html')
def second_page():
    """Redirect to the third page.
    """
    return Response(
        "Redirecting to third page...",
        status='301 Moved Permanently',
        headers=[('Location', url_for('third_page'))],
    )


@app.route('/third_page.html')
def third_page():
    """Show the third page of the web app."""
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


expected_dict = {
    'index.html':
            b"\n    <html>\n        <head>\n"
            + b"            <title>Hello world third page</title>\n"
            + b"        </head>\n        <body>\n            Page 3 !!!\n"
            + b"        </body>\n    </html>\n    ",

    'second_page.html':
            b"\n    <html>\n        <head>\n"
            + b"            <title>Hello world third page</title>\n"
            + b"        </head>\n        <body>\n            Page 3 !!!\n"
            + b"        </body>\n    </html>\n    ",

    'third_page.html':
            b"\n    <html>\n        <head>\n"
            + b"            <title>Hello world third page</title>\n"
            + b"        </head>\n        <body>\n            Page 3 !!!\n"
            + b"        </body>\n    </html>\n    "
}
