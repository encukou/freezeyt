from flask import Flask, Response, url_for

"""
Two different URLs can be freezed sometimes as same static file,
situation is difficult especially if there is redirection.
Freezeyt has to recognized URLs which are sharing one static file
as the output of freezing.
"""

app = Flask(__name__)

@app.route('/')
def index():
    return Response(
        "Redirecting to /index.html...",
        status='301 Moved Permanently',
        headers=[('Location', url_for('index_html'))],
)

@app.route('/index.html')
def index_html():
    return "This is /index.html route"


expected_dict = {'index.html': b"This is /index.html route"}

