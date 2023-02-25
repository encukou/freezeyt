from freezeyt import freeze, UnexpectedStatus
from freezeyt.freezer import Freezer
from fixtures.app_cleanup_config.app import app
from testutil import raises_multierror_with_one_exception


def test_cancel_tasks_was_called(monkeypatch):
    result = None
    async def fake_cancel_tasks(instance):
        nonlocal result
        result = 'cancelled'

    monkeypatch.setattr(Freezer, 'cancel_tasks', fake_cancel_tasks)
    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(app, {'output': {'type': 'dict'}})
    assert result == 'cancelled'
