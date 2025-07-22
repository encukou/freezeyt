from flask import Flask, redirect

app = Flask(__name__)
freeze_config = {'status_handlers': {'3xx': 'follow'}}


@app.route('/')
def index():
    return redirect('https://somewhere.invalid/')
