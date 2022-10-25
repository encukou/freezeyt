from werkzeug.test import Client
import freezegun

import pytest

from freezeyt.middleware import Middleware
from freezeyt.util import WrongMimetypeError

from testutil import APP_NAMES, context_for_test

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
    with context_for_test(app_name) as module:
        app = module.app
        config = getattr(module, 'freeze_config', {})

        app_client = Client(app)
        mw_client = Client(Middleware(app, config))

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
            if 'extra_files' in config:
                # extra_files is a Freezeyt-only setting, not visible
                # in the app. The mimetype of extra files might not match.
                expected_error = WrongMimetypeError
            for url in urls_from_expected_dict(expected_dict):
                check_responses_are_same(
                    app_client, mw_client, url,
                    expected_error=expected_error,
                )

def check_responses_are_same(app_client, mw_client, url, expected_error=()):
    app_response = app_client.get(url)
    print(app_response)
    print(app_response.get_data())
    try:
        mw_response = mw_client.get(url)
    except expected_error:
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
