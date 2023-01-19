from flask import Flask, url_for


class TestFailFastError(ValueError):
    """
    Error defined for purpose of this test to indetify source of exception easily.
    """


app = Flask(__name__)
freeze_config = {'fail_fast': True}
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/')
def index():
    return f"""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <a href="{url_for('invoke_error')}">Link</a>
            <a href="{url_for('invoke_error2')}">Link</a>
        </body>
    </html>
    """

@app.route('/value_error')
def invoke_error():
    raise TestFailFastError()

@app.route('/value_error2')
def invoke_error2():
    raise TestFailFastError()

