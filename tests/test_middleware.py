from werkzeug.test import Client

import pytest

from freezeyt.middleware import Middleware

from testutil import APP_NAMES, context_for_test


@pytest.mark.parametrize('app_name', APP_NAMES)
def test_middleware_doesnt_change_app(app_name):
    with context_for_test(app_name) as module:
        app = module.app

        app_client = Client(app)
        mw_client = Client(Middleware(app, {}))

        app_response = app_client.get('/')
        mw_response = mw_client.get('/')

        assert app_response.status == mw_response.status
        assert app_response.headers == mw_response.headers
        assert app_response.get_data() == mw_response.get_data()
