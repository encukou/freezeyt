from freezeyt import freeze, UnexpectedStatus
from freezeyt.freezer import Freezer
from freezeyt.filesaver import FileSaver
from fixtures.app_cleanup_config.app import app
from testutil import raises_multierror_with_one_exception, MultiError
import asyncio
import pytest


def test_cancel_tasks_was_called(monkeypatch):
    result = None
    async def fake_cancel_tasks(instance):
        nonlocal result
        result = 'called'

    monkeypatch.setattr(Freezer, 'cancel_tasks', fake_cancel_tasks)
    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(app, {'output': {'type': 'dict'}})
    assert result == 'called'


def test_cancellederror_was_raised(monkeypatch, tmp_path):
    NUM_PAGES = 50
    cancelled_error = None
    currently_processed_pages = 0

    async def fake_func(*args, **kwargs):
        nonlocal cancelled_error
        nonlocal currently_processed_pages
        if currently_processed_pages == NUM_PAGES:
            raise ValueError()
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelled_error = "yes"
            raise
 
    monkeypatch.setattr(FileSaver, 'save_to_filename', fake_func, raising=True)

    class ResultIterator:
        def __init__(self):
            self.contents = iter([b'a', b'b'])
        def __iter__(self):
            return self
        def __next__(self):
            result = next(self.contents)
            return result
        def close(self):
            ...

    def app(environ, start_response):
        nonlocal currently_processed_pages
        currently_processed_pages += 1
        print("currently_processed_pages", currently_processed_pages)
        start_response('200 OK', [('Content-type', 'text/html')])

    config = {
        'output': str(tmp_path),
        'extra_pages': [f'{n}.html' for n in range(NUM_PAGES)],
    }
    with pytest.raises(MultiError):
        freeze(app, config)
    assert cancelled_error == "yes"
