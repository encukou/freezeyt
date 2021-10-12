"""Test that the configuration of status_handlers work properly"""

import pytest

from flask import Flask, Response

from freezeyt import freeze, UnexpectedStatus


STATUSES = ('100', '201', '204', '301', '406', '503')

@pytest.mark.parametrize('response_status', STATUSES)
def test_error_handler(response_status):
    app = Flask(__name__)
    config = {
        'output': {'type': 'dict'},
        'status_handlers': {f'{response_status[0]}xx': 'error'},
    }

    @app.route('/')
    def index():
        return Response(response='Hello world!', status=response_status)

    with pytest.raises(UnexpectedStatus) as e:
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
        f"WARNING: URL http://localhost:8000/,"
        f" status code: {response_status} was freezed\n"
    )

    freeze(app, config)
    captured = capsys.readouterr()

    assert expected_output in captured.out


@pytest.mark.parametrize('response_status', STATUSES)
def test_default_handlers(response_status):
    app = Flask(__name__)
    config = {
        'output': {'type': 'dict'},
    }

    @app.route('/')
    def index():
        return Response(response='Hello world!', status=response_status)

    with pytest.raises(UnexpectedStatus) as e:
        freeze(app, config)

    assert e.value.status[:3] == f'{response_status}'
