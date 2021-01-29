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

expected_dict = {
    'index.html':
        b"\n    <html>\n        <head>\n            <title>Hello worl"
        + b"d</title>\n        </head>\n        <body>\n            He"
        + b"llo world!\n            <br>\n            <a href='/users/'>L"
        + b"INK</a> to user list.\n        </body>\n    </html>\n    ",

    'users':{
        'index.html':
            b"\n    <html>\n        <head>\n"
            + b"            <title>User List</title>\n        </head>\n"
            + b"        <body>\n            Users:\n            <ul>\n"
            + b"                <li><a href='a/'>User A</a></li>\n"
            + b"                <li><a href='b/'>User B</a></li>\n"
            + b"            </ul>\n        </body>\n    </html>\n    ",

        'a': {
            'index.html':
                b"\n    <html>\n        <head>\n"
                + b"            <title>User a</title>\n        </head>\n"
                + b"        <body>\n            Page for user a\n"
                + b"        </body>\n    </html>\n    "
        },
        'b': {
            'index.html':
                b"\n    <html>\n        <head>\n"
                + b"            <title>User b</title>\n        </head>\n"
                + b"        <body>\n            Page for user b\n"
                + b"        </body>\n    </html>\n    "
        },
    },

}