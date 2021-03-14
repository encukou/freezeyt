from bottle import Bottle

app = Bottle()
no_expected_directory = True

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Hello world app</title>
        </head>
        <body>
            <h3>Hello world! This is a home page of app.</h3>
            <div>
            <a href='/second_page.html'>LINK</a> to second page.
            </div>
        </body>
    </html>
    """

@app.route('/second_page.html')
def second_page():
    return """
    <html>
        <head>
            <title>Hello world app</title>
        </head>
        <body>
            <h3>Hello world! This is a second page of app.</h3>
        </body>
    </html>
    """


expected_dict = {
    'index.html':
        b"\n    <html>\n        <head>\n            "
        + b"<title>Hello world app</title>\n        </head>\n        <body>\n"
        + b"            <h3>Hello world! This is a home page of app.</h3>\n"
        + b"            <div>\n            <a href='/second_page.html'>LINK"
        + b"</a> to second page.\n            </div>\n        </body>\n"
        + b"    </html>\n    ",

    'second_page.html':
        b"\n    <html>\n        <head>\n            "
        + b"<title>Hello world app</title>\n        </head>\n        <body>\n"
        + b"            <h3>Hello world! This is a second page of app.</h3>\n"
        + b"        </body>\n"
        + b"    </html>\n    ",
}