from werkzeug.test import Client

import pytest

from freezeyt.middleware import Middleware

from testutil import APP_NAMES, context_for_test

def urls_from_expected_dict(expected_dict, prefix=''):
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
def test_middleware_doesnt_change_app(app_name):
    with context_for_test(app_name) as module:
        app = module.app
        config = getattr(module, 'freeze_config', {})

        app_client = Client(app)
        mw_client = Client(Middleware(app, config))

        check_responses_are_same(app_client, mw_client, '/')

        if app_name in ('app_static_tree', 'app_with_extra_files'):
            return

        try:
            expected_dict = module.expected_dict
        except AttributeError:
            pass
        else:
            for url in urls_from_expected_dict(expected_dict):
                check_responses_are_same(app_client, mw_client, url)

def check_responses_are_same(app_client, mw_client, url):
    app_response = app_client.get(url)
    mw_response = mw_client.get(url)

    assert app_response.status == mw_response.status
    assert app_response.headers == mw_response.headers
    assert app_response.get_data() == mw_response.get_data()
