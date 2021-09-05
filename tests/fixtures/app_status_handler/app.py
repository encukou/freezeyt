from flask import Flask

app = Flask(__name__)
freeze_config = {
        'status_handlers':
            {
                '202': 'warn',
                '301': 'follow',
                '404': 'ignore',
                '418': 'my_module:custom_handler',
                '429': 'ignore',
                '5xx': 'error',
            },
    }

@app.route('/')
def index():
    """Show index page of the web app.

    And link to the second page.
    """
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href='/not_found.html'>LINK</a> to page with status '404 NOT FOUND'.
        </body>
    </html>
    """

expected_dict = {
    'index.html':
            b"\n    <html>\n        <head>\n            <title>Hell"
            + b"o world</title>\n        </head>\n        <body>\n"
            + b"            Hello world!\n            <br>\n"
            + b"            <a href='/not_found.html'>LINK</a> t"
            + b"o page with status '404 NOT FOUND'.\n        "
            + b"</body>\n    </html>\n    ",

}