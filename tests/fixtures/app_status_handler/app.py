from flask import Flask, Response

from freezeyt.freezer import IgnorePage
from freezeyt.hooks import TaskInfo


def custom_status_handler(status: str, task: TaskInfo) -> None:
    task.freeze_info.add_url('http://localhost:8000/404.html')
    raise IgnorePage()


app = Flask(__name__)
freeze_config = {
        'status_handlers':
            {
                '204': 'ignore',
                '418': 'warn',
                '404': f'{__name__}:custom_status_handler',
            },
    }

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
            <a href='/page_not_exist.html'>LINK</a> to page '404 NOT FOUND'.
            <a href='/second_page.html'>LINK</a> to second page.
            <a href='/third_page.html'>LINK</a> to third page.
            <a href='/teapot.html'>LINK</a> to teapot.
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
        </body>
    </html>
    """

@app.route('/third_page.html')
def third_page():
    return Response(response='No content...', status='204 No Content')

@app.route('/teapot.html')
def teapot_page():
    return Response(response='I am a teapot...', status="418 I'm a teapot")

@app.route('/404.html')
def not_found_page():
    return """
    <html>
        <head>
            <title>404 NOT FOUND</title>
        </head>
        <body>
            404 PAGE NOT FOUND!
        </body>
    </html>
    """

expected_dict = {
    'index.html':
            b"\n    <html>\n        <head>\n            <title>Hell"
            + b"o world</title>\n        </head>\n        <body>\n"
            + b"            Hello world!\n            <br>\n"
            + b"            <a href='/page_not_exist.html'>LINK</a> t"
            + b"o page '404 NOT FOUND'.\n"
            + b"            <a href='/second_page.html'>LINK</a>"
            + b" to second page.\n"
            + b"            <a href='/third_page.html'>LINK</a> to third page.\n"
            + b"            <a href='/teapot.html'>LINK</a> to teapot.\n"
            + b"        </body>\n    </html>\n    ",

    'second_page.html':
            b"\n    <html>\n        <head>\n            <title>"
            + b"Hello world second page</title>\n        </head>\n"
            + b"        <body>\n            Second page !!!\n"
            + b"        </body>\n    </html>\n    ",

    'teapot.html': b"I am a teapot...",

    '404.html':
        b"\n    <html>\n        <head>\n            <title>"
        + b"404 NOT FOUND</title>\n        </head>\n"
        + b"        <body>\n            404 PAGE NOT FOUND!\n"
        + b"        </body>\n    </html>\n    ",

}
