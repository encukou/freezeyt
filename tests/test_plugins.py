from freezeyt import freeze
from testutil import context_for_test


def test_simple_plugin():
    recorded_calls = []

    def record_call(freeze_info):
        recorded_calls.append(freeze_info)

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'plugins': [record_call],
        }

        freeze(module.app, config)

    assert len(recorded_calls) == 1


def test_plugin_with_hook():
    recorded_calls = []

    def record_call(task_info):
        recorded_calls.append(task_info)

    def plugin(freeze_info):
        freeze_info.add_hook('page_frozen', record_call)

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'plugins': [plugin],
        }

        freeze(module.app, config)

    assert len(recorded_calls) == 2
