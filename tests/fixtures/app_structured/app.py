from flask import Flask

app = Flask(__name__)


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
            <a href='/users/'>LINK</a> to user list.
        </body>
    </html>
    """


@app.route('/users/')
def user_list():
    return """
    <html>
        <head>
            <title>User List</title>
        </head>
        <body>
            Users:
            <ul>
                <li><a href='a/'>User A</a></li>
                <li><a href='b/'>User B</a></li>
            </ul>
        </body>
    </html>
    """


@app.route('/users/<username>/')
def user(username):
    return f"""
    <html>
        <head>
            <title>User {username}</title>
        </head>
        <body>
            Page for user {username}
        </body>
    </html>
    """
