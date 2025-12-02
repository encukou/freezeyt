import werkzeug
from starlette.testclient import TestClient as StarletteTestClient
from werkzeug.test import Client as WSGITestClient
from werkzeug.datastructures import Headers
import freezegun
from flask import Flask, request
from packaging.version import Version

import pytest

from freezeyt.asgi_middleware import ASGIMiddleware
from freezeyt.util import WrongMimetypeError

from testutil import APP_NAMES, context_for_test, FIXTURES_PATH


class ASGITestClient:
    def __init__(self, app):
        self._client = StarletteTestClient(app, base_url='http://localhost:80')

    def open(self, url, *, method, data=b''):
        httpx_response = self._client.request(method, url, follow_redirects=False, content=data)
        return ASGITestClientResponse(httpx_response)

    # add specific methods: get, head, ...
    for method in 'get head options post send put'.split():
        def _func(self, *args, method=method, **kwargs):
            return self.open(*args, method=method, **kwargs)
        _func.__name__ = method
        locals()[method] = _func

class ASGITestClientResponse:
    def __init__(self, httpx_response):
        self._httpx_response = httpx_response
        code = httpx_response.status_code
        self.status = f'{code} {httpx_response.reason_phrase}'
        self.headers = Headers(httpx_response.headers)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        pass

    def get_data(self):
        return self._httpx_response.content

def urls_from_expected_dict(expected_dict, prefix=''):
    """Generate URLs from an `expected_dict` found in tests

    See test_urls_from_expected_dict for examples
    """
    for name, value in expected_dict.items():
        if isinstance(value, bytes):
            if name == 'index.html':
                yield prefix + '/'
            else:
                yield prefix + '/' + name
        else:
            new_prefix = prefix + '/' + name
            yield from urls_from_expected_dict(value, prefix=new_prefix)

def test_urls_from_expected_dict():
    """Test the test helper, urls_from_expected_dict"""
    assert sorted(urls_from_expected_dict(
        {
            'index.html': b'...',
            'other.html': b'...',
            'extra': {
                'index.html': b"...",
            },
            'extra2': {'index.html': b'Extra page 2'},
            'extra3': {'index.html': b'Extra page 3'},
            'extra4': {'index.html': b'Extra page 4'},
            'extra5': {'index.html': b'Extra page 5'},
            'extra6': {'index.html': b'Extra page 6', 'other.html': b'...'},
        }
    )) == [
        '/', '/extra/', '/extra2/', '/extra3/', '/extra4/', '/extra5/',
        '/extra6/', '/extra6/other.html', '/other.html',
    ]
    assert sorted(urls_from_expected_dict(
        {
            'index.html': b"...",
            'users':{
                'index.html': b"...",
                'a': {
                    'index.html': b"...",
                },
                'b': {
                    'index.html': b"...",
                },
            },

        }
    )) == [
        '/', '/users/', '/users/a/', '/users/b/',
    ]


@pytest.mark.parametrize('app_name', APP_NAMES)
@freezegun.freeze_time()  # freeze time so that Date headers don't change
def test_middleware_doesnt_change_app(app_name):
    if app_name in {'app_double_response_start'}:
        pytest.skip('app triggers extra check in WSGI-to-ASGI middleware')

    app_path = FIXTURES_PATH / app_name
    error_path = app_path / 'error.txt'
    with context_for_test(app_name) as module:
        app = module.app
        config = getattr(module, 'freeze_config', {})

        if config.get('app_interface', 'wsgi') == 'asgi':
            app_client = ASGITestClient(app)
        else:
            app_client = WSGITestClient(app)
        try:
            mw_client = ASGITestClient(ASGIMiddleware(app, config))
        except ValueError:
            # If creating the ASGIMiddleware fails, it should raise the same
            # exception as freezing the app.
            # Currently, only ValueError can be raised in the initialization
            assert error_path.exists()
            assert error_path.read_text().strip() == 'ValueError'
            return  # test was successful

        # Check that the middleware doesn't change the response
        # for /nonexisting_url/, except possibly raising WrongMimetypeError
        check_responses_are_same(
            app_client, mw_client, '/nonexisting_url/',
            expected_error=WrongMimetypeError,
        )

        try:
            expected_dict = module.expected_dict
        except AttributeError:
            # If expected_dict is not available, the app probably tests
            # that freezing fails.
            # Only check that the middleware doesn't change the homepage.
            check_responses_are_same(app_client, mw_client, '/')
        else:
            # By default, we don't expect any errors.
            expected_error = ()
            for url in urls_from_expected_dict(expected_dict):
                check_responses_are_same(
                    app_client, mw_client, url,
                    expected_error=expected_error,
                    expect_extra_files=('extra_files' in config),
                )

def check_responses_are_same(
    app_client, mw_client, url, expected_error=(), expect_extra_files=False,
):
    with app_client.get(url) as app_response:
        try:
            mw_response = mw_client.get(url)
        except expected_error:
            return

        with mw_response:
            if (expect_extra_files
                and app_response.status.startswith('404')
                and mw_response.status.startswith('200')
            ):
                # expected extra page
                return

            assert get_status_code(app_response.status) == get_status_code(mw_response.status)
            assert app_response.headers == mw_response.headers
            assert app_response.get_data() == mw_response.get_data()


def get_status_code(phrase):
    code = int(phrase[:3])
    assert str(code) == phrase[:3]
    return code


def test_middleware_rejects_wrong_mimetype():
    with context_for_test('app_wrong_mimetype') as module:
        app = module.app
        mw_client = ASGITestClient(ASGIMiddleware(app, {}))

        with pytest.raises(WrongMimetypeError):
            mw_client.get('/image.jpg')

        # Non-GET requests aren't checked
        mw_client.post('/image.jpg')
        mw_client.put('/image.jpg')


def test_middleware_tricky_extra_files():
    with context_for_test('tricky_extra_files') as module:
        app = module.app
        mw_client = ASGITestClient(ASGIMiddleware(app, module.freeze_config))

        # This file is looked up in static_dir:
        with mw_client.get('/static/file.txt') as response:
            assert response.status.startswith('200')

        # This file doesn't exist in static_dir; we shouldn't request it
        # from the app
        with mw_client.get('/static/missing.html') as response:
            assert response.status.startswith('404')

        # This page should be requested from the app (where it exists)
        with mw_client.get('/static-not.html') as response:
            assert response.status.startswith('200')

        # This page should also be requested from the app; but it doesn't
        # exist there.
        with mw_client.get('/static-not-missing.html') as response:
            assert response.status.startswith('404')

        # When getting a directory, there are several things Freezeyt could do:
        # - look for index.html, and serve it if found
        # - generate an index of the files in this directory
        # - fail with 404
        # It should do the same thing whether or not there's a trailing slash,
        # or one version could redirect to the other.
        with mw_client.get('/static') as response:
            assert response.status.startswith('404')
        with mw_client.get('/static/') as response:
            assert response.status.startswith('404')

        # Same as above, but in this case werkzeug.routing.Map returns a
        # redirect to '/static/etc/passwd' before ASGIMiddleware gets a chance
        # to return `403 Forbidden`. This is a detail that might change in
        # the future, so just assert that this isn't successful.
        with mw_client.get('/static//etc/passwd') as response:
            assert not response.status.startswith('200')

        # Looking outside the static directory is forbidden
        # This can't be done using the Starlette/httpx client, which normalizes
        # paths for us.
        pytest.skip()
        with mw_client.get('http://localhost/static/../app.py') as response:
            assert response.status.startswith('403')


DYNAMIC_METHODS = 'POST', 'PUT', 'PATCH', 'DELETE'
@pytest.mark.parametrize('method', DYNAMIC_METHODS)
def test_static_mode_disallows_methods(method):
    config = {
        'static_mode': True,
    }
    app = Flask(__name__)

    @app.route('/index.html', methods=('GET', *DYNAMIC_METHODS))
    def index():
        return 'OK'

    # Test the test app (behaviour without the ASGIMiddleware)
    app_client = WSGITestClient(app)
    assert app_client.open('/index.html', method='GET').status.startswith('200')
    assert app_client.open('/index.html', method=method).status.startswith('200')

    # Test behaviour with ASGIMiddleware
    mw_client = ASGITestClient(ASGIMiddleware(app, config))
    assert mw_client.open('/index.html', method='GET').status.startswith('200')

    # HTTP status 405: Method Not Allowed
    assert mw_client.open('/index.html', method=method).status.startswith('405')

@pytest.mark.parametrize('path', ('/index.html', '*'))
def test_static_mode_options(path):
    config = {
        'static_mode': True,
    }
    app = Flask(__name__)
    @app.route('/index.html')
    def index():
        return 'OK'
    mw_client = ASGITestClient(ASGIMiddleware(app, config))

    response = mw_client.options(path)
    assert response.status.startswith('200')
    assert response.get_data() == b''

    # Werkzeug's response headers were fixed in 2.2.0,
    # see https://github.com/pallets/werkzeug/issues/2450
    try:
        import importlib.metadata
    except ImportError:
        werkzeug_version = werkzeug.__version__
    else:
        werkzeug_version = importlib.metadata.version("werkzeug")
    if Version(werkzeug_version) >= Version('2.2.0'):
        assert response.headers == Headers({'Allow': 'GET, HEAD, OPTIONS'})
    else:
        assert response.headers['Allow'] == 'GET, HEAD, OPTIONS'

@pytest.mark.parametrize('app_name', APP_NAMES)
@freezegun.freeze_time()  # freeze time so that Date headers don't change
def test_static_mode_head(app_name):

    with context_for_test(app_name) as module:
        try:
            expected_dict = module.expected_dict
        except AttributeError:
            # If expected_dict is not available, the app probably tests
            # that freezing fails.
            # Skip it.
            pytest.skip()

        app = module.app
        config = {
            **getattr(module, 'freeze_config', {}),
            'static_mode': True,
        }
        if config.get('app_interface', 'wsgi') == 'asgi':
            app_client = ASGITestClient(app)
        else:
            app_client = WSGITestClient(app)
        mw_client = ASGITestClient(ASGIMiddleware(app, config))

        for url in urls_from_expected_dict(expected_dict):
            with app_client.get(url) as app_response:
                with mw_client.head(url) as mw_response:
                    assert get_status_code(mw_response.status) == get_status_code(app_response.status)
                    assert mw_response.headers == app_response.headers
                    assert mw_response.get_data() == b''

def test_parameter_removal():
    config = {
        'static_mode': True,
    }

    # An app that returns the parameters it gets as the response body
    app = Flask(__name__)
    @app.route('/')
    def echo_params():
        return request.query_string

    # Ensure the app works
    app_client = WSGITestClient(app)
    app_response = app_client.get('/?a=b')
    assert app_response.get_data() == b'a=b'

    # Ensure the middleware deletes parameters
    mw_client = ASGITestClient(ASGIMiddleware(app, config))
    mw_response = mw_client.get('/?a=b')
    assert mw_response.get_data() == b''

def test_request_body_removal():
    config = {
        'static_mode': True,
    }

    # An app that returns the request body it gets as the response body
    app = Flask(__name__)
    @app.route('/')
    def echo_body():
        return request.get_data()

    # Ensure the app works
    app_client = WSGITestClient(app)
    app_response = app_client.get('/', data=b'abc')
    assert app_response.get_data() == b'abc'

    # Ensure the middleware deletes parameters
    mw_client = ASGITestClient(ASGIMiddleware(app, config))
    mw_response = mw_client.get('/', data='abc')
    assert mw_response.get_data() == b''

