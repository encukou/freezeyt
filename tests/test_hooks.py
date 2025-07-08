from flask import Flask
import pytest

from freezeyt import freeze, ExternalURLError, UnexpectedStatus, MultiError
from testutil import context_for_test
from testutil import raises_multierror_with_one_exception


app = Flask(__name__)

def test_page_frozen_hook():
    recorded_tasks = {}

    def record_page(task_info):
        recorded_tasks[task_info.get_a_url()] = task_info

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'page_frozen': [record_page]},
        }

        freeze(module.app, config)

    print(recorded_tasks)

    assert len(recorded_tasks) == 2

    info = recorded_tasks['http://example.com/']
    assert info.path == 'index.html'

    info = recorded_tasks['http://example.com/second_page.html']
    assert info.path == 'second_page.html'


def test_success_hook():
    hook_called = False
    def start_hook(freezeinfo):
        nonlocal hook_called
        hook_called = True

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'https://jiri.one/',
            'hooks': {'success': [start_hook]},
        }

        output = freeze(module.app, config)
        assert hook_called
        assert output == module.expected_dict


_recorded_hook_calls = []
def hook(task_info):
    _recorded_hook_calls.append(task_info)


def test_page_frozen_hook_by_name():
    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'page_frozen': [f'{__name__}:hook']},
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
            'hooks': {'start': [start_hook]},
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
            'hooks': {'start': [start_hook]},
        }

        with pytest.raises(ExternalURLError):
            freeze(module.app, config)


@pytest.mark.parametrize(
    ['reason', 'expected_reasons'],
    (
        ('added for the test', ['added for the test']),
        (None, []),
    ),
)
def test_freezeinfo_add_404_url(reason, expected_reasons):
    hook_called = False
    def start_hook(freezeinfo):
        nonlocal hook_called
        hook_called = True

        freezeinfo.add_url(
            'http://example.com/404-page.html',
            reason=reason,
        )

    with context_for_test('app_with_extra_page') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'start': [start_hook]},
        }

        with raises_multierror_with_one_exception(UnexpectedStatus) as e:
            freeze(module.app, config)
        assert e.freezeyt_task.reasons == expected_reasons


@pytest.mark.parametrize('policy', ('save', 'follow'))
def test_page_frozen_hook_with_redirects(policy):
    recorded_tasks = []

    def record_page(task_info):
        recorded_tasks.append(task_info.path)

    with context_for_test('app_redirects') as module:
        config = dict(module.freeze_config)
        config['output'] = {'type': 'dict'}
        config['hooks'] = {'page_frozen': [record_page]}
        config['redirect_policy'] = policy
        output = freeze(module.app, config)

    output_paths = []
    def add_output_to_output_paths(dict_to_add, path_so_far):
        for key, value in dict_to_add.items():
            if isinstance(value, bytes):
                output_paths.append(path_so_far + key)
            else:
                add_output_to_output_paths(value, path_so_far + key + '/')
    add_output_to_output_paths(output, '')

    recorded_tasks.sort()
    output_paths.sort()

    assert recorded_tasks == output_paths


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
                'start': [start_hook],
                'page_frozen': [page_frozen_hook],
            },
        }

        freeze(module.app, config)

    a, b = freezeinfos
    assert a is b


def test_add_hook():
    recorded_tasks = {}

    def register_hook(freeze_info):
        freeze_info.add_hook('page_frozen', record_page)

    def record_page(task_info):
        recorded_tasks[task_info.get_a_url()] = task_info

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'start': [register_hook]},
        }

        freeze(module.app, config)

    print(recorded_tasks)

    assert len(recorded_tasks) == 2

    info = recorded_tasks['http://example.com/']
    assert info.path == 'index.html'

    info = recorded_tasks['http://example.com/second_page.html']
    assert info.path == 'second_page.html'


def test_multiple_hooks():
    recorded_tasks = {}
    counter = 0

    def record_page(task_info):
        recorded_tasks[task_info.get_a_url()] = task_info

    def increment_counter(task_info):
        nonlocal counter
        counter += 1

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {'page_frozen': [record_page, increment_counter]},
        }

        freeze(module.app, config)

    print(recorded_tasks)

    assert len(recorded_tasks) == 2
    assert counter == 2

    info = recorded_tasks['http://example.com/']
    assert info.path == 'index.html'

    info = recorded_tasks['http://example.com/second_page.html']
    assert info.path == 'second_page.html'


def check_task_counts(freeze_info, expected_total):
    total = freeze_info.total_task_count
    done = freeze_info.done_task_count
    failed = freeze_info.failed_task_count
    assert 0 <= failed <= done <= total <= expected_total


def test_task_counts():
    recorded_counts = []
    expected_total = 2

    def record_start(freeze_info):
        check_task_counts(freeze_info, expected_total)
        recorded_counts.append((
            '(start)',
            freeze_info.total_task_count,
            freeze_info.done_task_count,
        ))

    def record_page(task_info):
        check_task_counts(task_info.freeze_info, expected_total)
        recorded_counts.append((
            task_info.path,
            task_info.freeze_info.total_task_count,
            task_info.freeze_info.done_task_count,
        ))

    with context_for_test('app_2pages') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {
                'start': [record_start],
                'page_frozen': [record_page],
            },
        }

        freeze(module.app, config)

    print(recorded_counts)

    assert recorded_counts == [
        ('(start)', 1, 0),
        ('index.html', 2, 1),
        ('second_page.html', 2, 2),
    ]


def test_task_counts_extra_page():
    recorded_done_counts = []
    recorded_paths = set()
    expected_total = 3

    def record_start(freeze_info):
        check_task_counts(freeze_info, expected_total)
        assert freeze_info.done_task_count == 0

    def record_page(task_info):
        check_task_counts(task_info.freeze_info, expected_total)
        recorded_done_counts.append(task_info.freeze_info.done_task_count)
        recorded_paths.add(task_info.path)

    with context_for_test('app_with_extra_page_deep') as module:
        config = {
            **module.freeze_config,
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {
                'start': [record_start],
                'page_frozen': [record_page],
            },
        }

        freeze(module.app, config)

    assert recorded_done_counts == [1, 2, 3]
    assert recorded_paths == {
        'index.html', 'extra/index.html', 'extra/extra_deep/index.html',
    }


def test_task_counts_extra_file():
    recorded_done_counts = []
    recorded_paths = set()
    expected_total = 7

    def record_start(freeze_info):
        check_task_counts(freeze_info, expected_total)
        assert freeze_info.done_task_count == 0

    def record_page(task_info):
        check_task_counts(task_info.freeze_info, expected_total)
        recorded_done_counts.append(task_info.freeze_info.done_task_count)
        recorded_paths.add(task_info.path)

    with context_for_test('app_with_extra_files') as module:
        config = {
            **module.freeze_config,
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {
                'start': [record_start],
                'page_frozen': [record_page],
            },
        }

        freeze(module.app, config)

    assert recorded_done_counts == list(range(1, expected_total+1))
    assert recorded_paths == {
        'index.html', 'CNAME', '.nojekyll', 'config/xyz',
        'smile.png', 'bin_range.dat', 'smile2.png',
    }


def test_page_failed_hook():
    records = []
    expected_total = 3

    def record_frozen(task_info):
        check_task_counts(task_info.freeze_info, expected_total)
        assert task_info.path == 'index.html'
        records.append((
            'frozen',
            task_info.freeze_info.total_task_count,
            task_info.freeze_info.done_task_count,
            task_info.freeze_info.failed_task_count,
        ))
        assert task_info.exception == None

    def record_fail(task_info):
        check_task_counts(task_info.freeze_info, expected_total)
        assert task_info.path in {'nowhere', 'also_nowhere'}
        records.append((
            'failed',
            task_info.freeze_info.total_task_count,
            task_info.freeze_info.done_task_count,
            task_info.freeze_info.failed_task_count,
        ))
        assert isinstance(task_info.exception, UnexpectedStatus)

    with context_for_test('app_2_broken_links') as module:
        config = {
            'output': {'type': 'dict'},
            'prefix': 'http://example.com/',
            'hooks': {
                'page_frozen': [record_frozen],
                'page_failed': [record_fail],
            },
        }

        with pytest.raises(MultiError):
            freeze(module.app, config)

    assert records == [
        ('frozen', 3, 1, 0),
        ('failed', 3, 2, 1),
        ('failed', 3, 3, 2),
    ]
