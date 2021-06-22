from flask import Flask
import pytest

from freezeyt import freeze, ExternalURLError
from testutil import context_for_test


app = Flask(__name__)

def test_page_frozen_hook():
    recorded_tasks = {}

    def record_page(task_info):
        recorded_tasks[task_info.get_a_url()] = task_info

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'page_frozen': record_page},
        }

        freeze(module.app, config)

    print(recorded_tasks)

    assert len(recorded_tasks) == 2

    info = recorded_tasks['http://example.com:80/']
    assert info.path == 'index.html'

    info = recorded_tasks['http://example.com:80/second_page.html']
    assert info.path == 'second_page.html'


_recorded_hook_calls = []
def hook(task_info):
    _recorded_hook_calls.append(task_info)


def test_page_frozen_hook_by_name():
    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'page_frozen': f'{__name__}:hook'},
        }

        _recorded_hook_calls.clear()
        freeze(module.app, config)
        assert len(_recorded_hook_calls) == 2


def test_freezeinfo_add_url():
    hook_called = False
    def start_hook(freezeinfo):
        nonlocal hook_called
        hook_called = True

        freezeinfo.add_url('http://example.com/extra/')

    with context_for_test('app_with_extra_page') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'start': start_hook},
        }

        output = freeze(module.app, config)
        assert hook_called
        assert output == module.expected_dict


def test_freezeinfo_add_external_url():
    hook_called = False
    def start_hook(freezeinfo):
        nonlocal hook_called
        hook_called = True

        freezeinfo.add_url('http://different-domain.example/extra/')

    with context_for_test('app_with_extra_page') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'start': start_hook},
        }

        with pytest.raises(ExternalURLError):
            freeze(module.app, config)


def test_taskinfo_has_freezeinfo():
    freezeinfos = []

    def start_hook(freezeinfo):
        freezeinfos.append(freezeinfo)

    def page_frozen_hook(pageinfo):
        freezeinfos.append(pageinfo.freeze_info)

    with context_for_test('app_simple') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {
                'start': start_hook,
                'page_frozen': page_frozen_hook,
            },
        }

        freeze(module.app, config)

    a, b = freezeinfos
    assert a is b
