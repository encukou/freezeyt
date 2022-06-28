
from werkzeug.test import Client

from freezeyt.middleware import Middleware

from fixtures.app_simple.app import app

def test_middleware_doesnt_change_app():
    app_client = Client(app)
    mw_client = Client(Middleware(app, {}))

    app_response = app_client.get('/')
    mw_response = mw_client.get('/')

    assert app_response.status == mw_response.status
    assert app_response.headers == mw_response.headers
    assert app_response.get_data() == mw_response.get_data()
