from flask import Flask, url_for

app = Flask(__name__)
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
            <a href="nowhere">Link to nowhere</a>
            <a href="{url_for('value_error')}">Link</a>
            <a href="{url_for('type_error')}">Link</a>
            <a href="{url_for('type_error2')}">Link</a>
        </body>
    </html>
    """

@app.route('/value_error')
def value_error():
    raise ValueError()

@app.route('/type_error')
def type_error():
    raise TypeError()

@app.route('/type_error2')
def type_error2():
    raise TypeError()
