"""Test that the configuration of status_handlers work properly"""

import pytest

from flask import Flask, Response

from freezeyt import freeze, UnexpectedStatus

from testutil import raises_multierror_with_one_exception, context_for_test


STATUSES = ('100', '200', '201', '300', '301', '400', '406', '500', '503', '888')

@pytest.mark.parametrize('response_status', STATUSES )
def test_error_handler(response_status):
    app = Flask(__name__)
    config = {
        'output': {'type': 'dict'},
        'status_handlers': {f'{response_status[0]}xx': 'error'},
    }

    @app.route('/')
    def index():
        return Response(response='Hello world!', status=response_status)

    with raises_multierror_with_one_exception(UnexpectedStatus) as e:
        freeze(app, config)

    assert e.value.status[:3] == f'{response_status}'


@pytest.mark.parametrize('response_status', STATUSES)
def test_warn_handler(capsys, response_status):
    app = Flask(__name__)
    config = {
        'output': {'type': 'dict'},
        'status_handlers': {f'{response_status[0]}xx': 'warn'},
    }

    @app.route('/')
    def index():
        return Response(response='Hello world!', status=response_status)

    expected_output = (
        f"[WARNING] URL http://localhost:8000/,"
        f" status code: {response_status} was freezed\n"
    )

    freeze(app, config)
    captured = capsys.readouterr()

    assert expected_output in captured.out


def test_several_warns(capsys):
    warnings = []

    def record_warnings(task_info):
        nonlocal warnings
        warnings = list(task_info._freezer.warnings)

    config = {
        'output': {'type': 'dict'},
        'status_handlers': {'200': 'warn'},
        'hooks': {'page_frozen': [record_warnings]},
    }

    with context_for_test("app_3pages_deep") as module:
        freeze(module.app, config)
        captured = capsys.readouterr()

    expected_output = (
        "[WARNING] URL http://localhost:8000/,"
        " status code: 200 was freezed\n"
        "[WARNING] URL http://localhost:8000/second_page.html,"
        " status code: 200 was freezed\n"
        "[WARNING] URL http://localhost:8000/third_page.html,"
        " status code: 200 was freezed\n"
    )
    expected_warnings = [
        'URL http://localhost:8000/, status code: 200 was freezed',
        'URL http://localhost:8000/second_page.html, status code: 200 was freezed',
        'URL http://localhost:8000/third_page.html, status code: 200 was freezed',
    ]

    assert expected_output == captured.out
    assert warnings == expected_warnings


@pytest.mark.parametrize('response_status', ['100', '201', '302', '404', '500'])
def test_default_handlers_error(response_status):
    app = Flask(__name__)
    config = {
        'output': {'type': 'dict'},
    }

    @app.route('/')
    def index():
        return Response(response='Hello world!', status=response_status)

    with raises_multierror_with_one_exception(UnexpectedStatus) as e:
        freeze(app, config)

    assert e.value.status[:3] == f'{response_status}'

hello_app = Flask(__name__)
@hello_app.route('/')
def index():
    return 'Hello world!'


def test_default_behaviour_status_200():
    config = {
        'output': {'type': 'dict'},
    }

    result = freeze(hello_app, config)
    assert result == {'index.html': b'Hello world!'}


def custom_handler(task):
    return "non_sense"

def test_error_custom_handler():
    config = {
        'output': {'type': 'dict'},
        'status_handlers': {'200': custom_handler}
    }

    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(hello_app, config)


def old_custom_ignore_handler(task):
    from freezeyt.status_handlers import ignore
    return ignore(task)

def test_old_custom_ignore_handler():
    config = {
        'output': {'type': 'dict'},
        'status_handlers': {'200': old_custom_ignore_handler}
    }

    with pytest.deprecated_call():
        result = freeze(hello_app, config)
    assert result == {}


def new_custom_ignore_handler(task):
    from freezeyt.actions import ignore
    return ignore(task)

def test_new_custom_ignore_handler():
    config = {
        'output': {'type': 'dict'},
        'status_handlers': {'200': new_custom_ignore_handler}
    }

    result = freeze(hello_app, config)
    assert result == {}

@pytest.mark.parametrize(
    'status',
    ['ldaskfjhfasdlkdasjh', '', '50x', '50', 50, 'xxx', 'a8xx', '123a'],
)
def test_bad_status(status):
    config = {
        'output': {'type': 'dict'},
        'status_handlers': {status: 'save'}
    }

    with pytest.raises((ValueError, TypeError)):
        freeze(hello_app, config)


def test_actions_from_header():
    app = Flask(__name__)
    @app.route('/')
    def index():
        return (
            '<a href="/ignore_me/">...</a><a href="/follow_me/">...</a>',
            '404 Ignore This Status',
            {'freezeyt-action': 'save'},
        )

    @app.route('/ignore_me/')
    def ignored_page():
        return 'ignored', {'freezeyt-action': 'ignore'}

    @app.route('/follow_me/')
    def followed_page():
        return Response(
            response='followed',
            status='404 Ignore This Status',
            headers={'freezeyt-action': 'follow', 'location': '/destination/'},
        )

    @app.route('/destination/')
    def destination_page():
        return 'destination'

    config = {
        'output': {'type': 'dict'},
    }

    result = freeze(app, config)
    assert result == {
        'index.html': b'<a href="/ignore_me/">...</a><a href="/follow_me/">...</a>',
        'follow_me': {
            'index.html': b'destination',
        },
        'destination': {
            'index.html': b'destination',
        },
    }


def test_warn_handler_from_header(capsys):
    app = Flask(__name__)
    config = {
        'output': {'type': 'dict'},
    }

    @app.route('/')
    def index():
        return Response(
            response='Hello world!',
            headers={'freezeyt-action': 'warn'},
        )

    expected_output = (
        "[WARNING] URL http://localhost:8000/, status code: 200 was freezed\n"
    )

    freeze(app, config)
    captured = capsys.readouterr()

    assert expected_output in captured.out


def test_error_handler_from_header():
    app = Flask(__name__)
    config = {
        'output': {'type': 'dict'},
    }

    @app.route('/')
    def index():
        return Response(
            response='Hello world!',
            headers={'freezeyt-action': 'error'},
        )

    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(app, config)
