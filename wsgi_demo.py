from wsgiref.simple_server import make_server

from demo_app import app

# with make_server("", 8000, app) as server:
#     print("Serving HTTP on port 8000...")

#     # Respond to requests until process is killed
#     server.serve_forever()


environ = {
    "SERVER_NAME": "localhost",
    "wsgi.url_scheme": "http",
    "SERVER_PORT": "8000",
    "REQUEST_METHOD": "GET",
    "PATH_INFO": "about",
    # ...
}


def start_response(status, headers):
    print("status", status)
    print("headers", headers)


result = app(environ, start_response)

for item in result:
    print(item)
