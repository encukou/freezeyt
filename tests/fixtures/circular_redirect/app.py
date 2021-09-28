from flask import Flask, redirect, url_for

app = Flask(__name__)
freeze_config = {
    'status_handlers': {'302': 'error'}
}


@app.route('/')
def index():
    """Show index page of the web app.

    And link to the second page.
    """
    return redirect(url_for('second_page'))


@app.route('/second_page.html')
def second_page():
    """Show the second page."""
    return redirect(url_for('index'))
