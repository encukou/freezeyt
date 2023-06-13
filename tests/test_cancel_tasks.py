from freezeyt import freeze, UnexpectedStatus
from freezeyt.freezer import Freezer, FileSaver
from fixtures.app_cleanup_config.app import app
from testutil import raises_multierror_with_one_exception
import sys
import asyncio
import pytest


def test_cancel_tasks_was_called(monkeypatch):
    result = None
    async def fake_cancel_tasks(instance):
        nonlocal result
        result = 'cancelled'

    monkeypatch.setattr(Freezer, 'cancel_tasks', fake_cancel_tasks)
    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(app, {'output': {'type': 'dict'}})
    assert result == 'cancelled'

if sys.version_info >= (3, 8):
    from unittest.mock import patch
    def test_cancel_tasks_was_called_with_mock():  
        with patch.object(Freezer, 'cancel_tasks', return_value=None) as mock_method:
            with raises_multierror_with_one_exception(UnexpectedStatus):
                freeze(app, {'output': {'type': 'dict'}})

        assert mock_method.called

def _x_test_all_tasks_were_canceled(monkeypatch, tmp_path):
    NUM_PAGES = 50
    cancelled_errors = 0
    currently_processed_pages = 0

    async def fake_func(*args, **kwargs):
        """Fake func for replace the save_to_filename method from FileSaver"""
        nonlocal cancelled_errors
        nonlocal currently_processed_pages
        if currently_processed_pages == NUM_PAGES:
            raise ValueError()
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelled_errors += 1
            raise

    monkeypatch.setattr(FileSaver, 'save_to_filename', fake_func, raising=True)

    def app(environ, start_response):
        nonlocal currently_processed_pages
        currently_processed_pages += 1
        start_response('200 OK', [('Content-type', 'text/html')])

    config = {
        'output': str(tmp_path),
        'extra_pages': [f'{n}.html' for n in range(NUM_PAGES)],
        'fail_fast': True}

    with pytest.raises(ValueError):
        freeze(app, config)
    assert cancelled_errors == NUM_PAGES
