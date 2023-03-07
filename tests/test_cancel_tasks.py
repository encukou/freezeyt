from freezeyt import freeze, UnexpectedStatus
from freezeyt.freezer import Freezer
from freezeyt.filesaver import FileSaver
from fixtures.app_cleanup_config.app import app
from testutil import raises_multierror_with_one_exception
import asyncio
import pytest
from unittest.mock import patch


def test_cancel_tasks_was_called():  
    with patch.object(Freezer, 'cancel_tasks', return_value=None) as mock_method:
        with raises_multierror_with_one_exception(UnexpectedStatus):
            freeze(app, {'output': {'type': 'dict'}})
    
    assert mock_method.called


def test_cancellederror_was_raised(monkeypatch, tmp_path):
    NUM_PAGES = 50
    cancelled_error = None
    currently_processed_pages = 0

    async def fake_func(*args, **kwargs):
        """Fake func for replace the save_to_filename method from FileSaver"""
        nonlocal cancelled_error
        nonlocal currently_processed_pages
        if currently_processed_pages == NUM_PAGES:
            raise ValueError()
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelled_error = "raised"
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
    assert cancelled_error == "raised"
