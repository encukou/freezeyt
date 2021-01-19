from flask import Flask, render_template

app = Flask(__name__)
freeze_config = {'extra_pages': ["/static/OFL.txt"]}


@app.route("/")
def index():
    """
    Demo app for test

    HTML template links to CSS which links to a font in a file.
    """
    return render_template("index.html")
