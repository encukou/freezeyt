from werkzeug.test import Client
import freezegun

import pytest

from freezeyt.middleware import Middleware
from freezeyt.util import WrongMimetypeError

from testutil import APP_NAMES, context_for_test, FIXTURES_PATH

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
    app_path = FIXTURES_PATH / app_name
    error_path = app_path / 'error.txt'
    with context_for_test(app_name) as module:
        app = module.app
        config = getattr(module, 'freeze_config', {})

        app_client = Client(app)
        try:
            mw_client = Client(Middleware(app, config))
        except ValueError:
            # If creating the Middleware fails, it should raise the same
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
            #if 'extra_files' in config:
                ## extra_files is a Freezeyt-only setting, not visible
                ## in the app. The mimetype of extra files might not match.
                #expected_error = WrongMimetypeError
            for url in urls_from_expected_dict(expected_dict):
                check_responses_are_same(
                    app_client, mw_client, url,
                    expected_error=expected_error,
                    expect_extra_files=('extra_files' in config),
                )

def check_responses_are_same(
    app_client, mw_client, url, expected_error=(), expect_extra_files=False,
):
    app_response = app_client.get(url)
    print(app_response)
    print(app_response.get_data())
    try:
        mw_response = mw_client.get(url)
    except expected_error:
        return

    if (expect_extra_files
        and app_response.status.startswith('404')
        and mw_response.status.startswith('200')
    ):
        # expected extra page
        return

    assert app_response.status == mw_response.status
    assert app_response.headers == mw_response.headers
    assert app_response.get_data() == mw_response.get_data()


def test_middleware_rejects_wrong_mimetype():
    with context_for_test('app_wrong_mimetype') as module:
        app = module.app
        mw_client = Client(Middleware(app, {}))

        with pytest.raises(WrongMimetypeError):
            mw_client.get('/image.jpg')


def test_middleware_tricky_extra_files():
    with context_for_test('tricky_extra_files') as module:
        app = module.app
        mw_client = Client(Middleware(app, module.freeze_config))

        # This file is looked up in static_dir:
        assert mw_client.get('/static/file.txt').status.startswith('200')

        # This file doesn't exist in static_dir; we shouldn't request it
        # from the app
        assert mw_client.get('/static/missing.html').status.startswith('404')

        # This page should be requested from the app (where it exists)
        assert mw_client.get('/static-not.html').status.startswith('200')

        # This page should also be requested from the app; but it doesn't
        # exist there.
        assert mw_client.get('/static-not-missing.html').status.startswith('404')

