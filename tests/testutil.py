from pathlib import Path
from contextlib import contextmanager
import sys
import importlib
import filecmp
import difflib

import pytest


FIXTURES_PATH = Path(__file__).parent / 'fixtures'

@contextmanager
def context_for_test(app_name):
    """Provide a context in which a testing app is imported

    The module with the app is available as the context manager
    object, for example:

        with context_for_test('demo_app') as module:
            wsgi_app = module.app
    """
    app_dir = FIXTURES_PATH / app_name
    sys.modules.pop('app', None)
    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.syspath_prepend(app_dir)
            module = importlib.import_module('app')
        yield module
    finally:
        sys.modules.pop('app', None)




def assert_dirs_same(got: Path, expected: Path):
    cmp = filecmp.dircmp(got, expected, ignore=[])
    cmp.report_full_closure()
    assert_cmp_same(cmp)


def assert_cmp_same(cmp):
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

