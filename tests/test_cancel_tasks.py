import asyncio
import sys

import pytest

from freezeyt import freeze, UnexpectedStatus
from freezeyt.compat import asyncio_Barrier
from freezeyt.freezer import Freezer, FileSaver
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

if sys.version_info >= (3, 8):
    from unittest.mock import patch
    def test_cancel_tasks_was_called_with_mock():  
        with patch.object(Freezer, 'cancel_tasks', return_value=None) as mock_method:
            with raises_multierror_with_one_exception(UnexpectedStatus):
                freeze(app, {'output': {'type': 'dict'}})

        assert mock_method.called

def test_fail_fast_cancels_tasks(monkeypatch, tmp_path):
    """Test that with fail_fast, tasks are cancelled after an error.

    This works by trying to save a lot of pages, one of which raises an error
    and the other ones take forever to complete.
    """
    NUM = 20
    N_CANCELLED_PAGES = NUM * 2 + 1  # includes index.html
    N_PAGES = N_CANCELLED_PAGES + 1  # includes index.html & error.html
    # (N_PAGES must be lower than freezer.MAX_RUNNING_TASKS)

    num_cancelled_errors = 0

    barrier = asyncio_Barrier(N_PAGES)

    async def fake_save_to_filename(self, filename, content_iterable):
        """Fake func for replace the save_to_filename method from FileSaver"""
        nonlocal num_cancelled_errors
        await barrier.wait() # wait for all tasks to reach this barrier
        if filename.name == 'error.html':
            raise ValueError()
        else:
            try:
                await asyncio.Event().wait()   # wait for cancellation
            except asyncio.CancelledError:
                num_cancelled_errors += 1
                raise

    monkeypatch.setattr(FileSaver, 'save_to_filename',
                        fake_save_to_filename, raising=True)

    def app(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/html')])
        return []

    config = {
        'output': str(tmp_path),
        'extra_pages': [
            # 'index.html' is frozen automatically
            *(f'before-{n}.html' for n in range(NUM)),  # N extra pages
            'error.html',  # this raises an error
            *(f'after-{n}.html' for n in range(NUM)),  # N extra pages
        ],
        'fail_fast': True}

    with pytest.raises(ValueError):
        freeze(app, config)

    assert num_cancelled_errors == N_CANCELLED_PAGES
