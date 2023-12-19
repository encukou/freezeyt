from pathlib import Path
from contextlib import contextmanager
import sys
import importlib
import filecmp
import difflib

import pytest

from freezeyt import MultiError


FIXTURES_PATH = Path(__file__).parent / 'fixtures'

APP_NAMES = [
    p.name
    for p in FIXTURES_PATH.iterdir()
    if (p / 'app.py').exists()
]

@contextmanager
def context_for_test(app_name, module_name='app'):
    """Provide a context in which a testing app is imported

    The module with the app is available as the context manager
    object, for example:

        with context_for_test('demo_app') as module:
            wsgi_app = module.app

    Imports done in the context are undone at the end.
    """
    app_dir = FIXTURES_PATH / app_name
    sys.modules.pop('app', None)
    original_modules = dict(sys.modules)
    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.syspath_prepend(app_dir)
            module = importlib.import_module(module_name)
        yield module
    finally:
        sys.modules.clear()
        sys.modules.update(original_modules)


def assert_dirs_same(got: Path, expected: Path) -> None:
    cmp = filecmp.dircmp(got, expected, ignore=[])
    cmp.report_full_closure()
    assert_cmp_same(cmp)


def assert_cmp_same(cmp: filecmp.dircmp) -> None:
    print('assert_cmp_same', cmp.left, cmp.right)

    if cmp.left_only:
        raise AssertionError(f'Extra files frozen: {cmp.left_only}')

    if cmp.right_only:
        raise AssertionError(f'Files not frozen: {cmp.right_only}')

    if cmp.common_funny:
        raise AssertionError(f'Funny differences: {cmp.common_funny}')

    # dircmp does "shallow comparison"; it only looks at file size and
    # similar attributes. So, files in "same_files" might actually
    # be different, and we need to check their contents.
    # Files in "diff_files" are checked first, so failures are reported
    # early.
    for filename in list(cmp.diff_files) + list(cmp.same_files):
        path1 = Path(cmp.left) / filename
        path2 = Path(cmp.right) / filename
        try:
            content1 = path1.read_text()
            content2 = path2.read_text()
        except UnicodeDecodeError:
            content1 = path1.read_bytes()
            content2 = path2.read_bytes()
        else:
            # Show a diff between actual and expected output
            diff = difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile='actual',
                tofile='expected',
            )
            for line in diff:
                print(line.rstrip('\n'))
        assert content1 == content2

    if cmp.diff_files:
        raise AssertionError(f'Files do not have expected content: {cmp.diff_files}')

    for subcmp in cmp.subdirs.values():
        assert_cmp_same(subcmp)


class ExceptionInfo:
    """Mimics pytest's ExceptionInfo class"""
    # ExceptionInfo (the result of pytest.raises)
    # doesn't have public API for creating instances.
    # This is a class that looks enough like it for our purposes:
    # the attributes are filled in when the
    # raises_multierror_with_one_exception context manager exits.

    # Additionally, this ExceptionInfo has a "freezeyt_task" attribute.

    value: Exception
    type: type
    freezeyt_task: object  # (TaskInfo)


@contextmanager
def raises_multierror_with_one_exception(exc_type):
    """Like pytest.raises, but expects a MultiError with a single exception

    The single exception must be of the given `exc_type`; information about it
    (and not the MultiError) is provided by this context manager.
    """
    excinfo = ExceptionInfo()
    with pytest.raises(MultiError) as multierror_excinfo:
        yield excinfo
    multierror = multierror_excinfo.value
    assert len(multierror.exceptions) == 1
    excinfo.value = multierror.exceptions[0]
    excinfo.type = type(multierror.exceptions[0])

    with pytest.raises(exc_type):
        raise excinfo.value

    assert len(multierror.tasks) == 1
    assert multierror.tasks[0].exception == multierror.exceptions[0]
    excinfo.freezeyt_task = multierror.tasks[0]
