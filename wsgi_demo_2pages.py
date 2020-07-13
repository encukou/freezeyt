from wsgiref.simple_server import make_server

from demo_app_2pages import app

with make_server('', 8000, app) as server:
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    server.serve_forever()
