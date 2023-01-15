from flask import Flask, url_for

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
            <a href="{url_for('value_error')}">Link</a>
            <a href="{url_for('value_error2')}">Link</a>
        </body>
    </html>
    """

@app.route('/value_error')
def value_error():
    raise ValueError()

@app.route('/value_error2')
def value_error2():
    raise ValueError()

