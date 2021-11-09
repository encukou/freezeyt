from freezeyt import freeze
from freezeyt.freezer import MAX_RUNNING_TASKS



def test_tasks_are_limited(tmp_path):
    NUM_PAGES = MAX_RUNNING_TASKS * 2
    currently_processed_pages = 0

    class ResultIterator:
        def __init__(self):
            self.contents = iter([b'a', b'b'])
        def __iter__(self):
            return self
        def __next__(self):
            assert currently_processed_pages <= MAX_RUNNING_TASKS
            result = next(self.contents)
            return result
        def close(self):
            nonlocal currently_processed_pages
            currently_processed_pages -= 1

    def app(environ, start_response):
        nonlocal currently_processed_pages
        currently_processed_pages += 1
        start_response('200 OK', [('Content-type', 'text/html')])
        return ResultIterator()

    config = {
        'output': str(tmp_path),
        'extra_pages': [f'{n}.html' for n in range(NUM_PAGES)],
    }

    freeze(app, config)
