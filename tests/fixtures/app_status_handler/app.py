from flask import Flask, Response

from freezeyt.hooks import TaskInfo


def custom_status_handler(task: TaskInfo) -> str:
    task.freeze_info.add_url('http://localhost:8000/EXTRA.html')
    return 'save'


app = Flask(__name__)
freeze_config = {
        'status_handlers':
            {
                '204': 'ignore',
                '418': 'warn',
                '404': 'ignore',
                '600': f'{__name__}:custom_status_handler',
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
    response_content = """
    <html>
        <head>
            <title>Hello world second page</title>
        </head>
        <body>
            Second page !!!
        </body>
    </html>
    """
    return Response(
        response=response_content, status='600 Custom Handler Used'
    )


@app.route('/third_page.html')
def third_page():
    return Response(response='No content...', status='204 No Content')

@app.route('/teapot.html')
def teapot_page():
    return Response(response='I am a teapot...', status="418 I'm a teapot")

@app.route('/EXTRA.html')
def not_found_page():
    return """
    <html>
        <head>
            <title>EXTRA</title>
        </head>
        <body>
            PAGE ADDED BY CUSTOM HANDLER!
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

    'EXTRA.html':
        b"\n    <html>\n        <head>\n            <title>"
        + b"EXTRA</title>\n        </head>\n"
        + b"        <body>\n            PAGE ADDED BY CUSTOM HANDLER!\n"
        + b"        </body>\n    </html>\n    ",

}
