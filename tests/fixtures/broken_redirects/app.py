from flask import Flask, redirect, url_for

app = Flask(__name__)
freeze_config = {}


@app.route('/')
def index():
    return f"""
        <a href="{url_for('circular')}">circular</a>
        <a href="{url_for('to_nonexistent')}">nonexistent</a>
        <a href="{url_for('to_external')}">external</a>
        <a href="{url_for('to_self')}">self</a>
        <a href="{url_for('without_location')}">without location</a>
    """


@app.route('/circular/')
def circular():
    return redirect(url_for('circular2'))


@app.route('/circular2/')
def circular2():
    return redirect(url_for('circular'))


@app.route('/to-nonexistent/')
def to_nonexistent():
    return redirect('nonexistent.wtf')


@app.route('/to-external/')
def to_external():
    return redirect('https://nowhere.invalid')


@app.route('/to-self/')
def to_self():
    return redirect(url_for('to_self'))


@app.route('/without-location/')
def without_location():
    return ('no location header!', 301)
