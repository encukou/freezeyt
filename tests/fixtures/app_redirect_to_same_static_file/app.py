from flask import Flask, Response, url_for

#Flask dynamic app can define for one static file
#different URLs with different content (e.g. '/', '/index.html'),
#It is complicated for Freezeyt as static server to disntict
#two different URLs for one static file.
#One content will be always lost.
#    In case of redirection ..... ????????

app = Flask(__name__)
freeze_config = {
    'status_handlers': {'3xx': 'follow'},
}

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

