import importlib
from pathlib import Path
import filecmp
import os
import shutil

import pytest

from freezeyt import freeze


FIXTURES_PATH = Path(__file__).parent / 'fixtures'
MODULE_NAMES = [p.stem for p in FIXTURES_PATH.iterdir() if p.is_file()]


@pytest.mark.parametrize('module_name', MODULE_NAMES)
def test_output(tmp_path, module_name):
    module = importlib.import_module(module_name)
    app = module.app

    freeze(app, tmp_path)

    # ../test_expected_output.py
    # ../fixtures/demo_app/
    expected = Path(__file__).parent / 'fixtures' / module_name

    if not expected.exists():
        if 'TEST_CREATE_EXPECTED_OUTPUT' in os.environ:
            shutil.copytree(tmp_path, expected)
        else:
            raise AssertionError(
                f'Expected output directory ({expected}) does not exist. '
                + f'Run with TEST_CREATE_EXPECTED_OUTPUT=1 to create it'
            )

    assert_dirs_same(tmp_path, expected)


def assert_dirs_same(got: Path, expected: Path):
    cmp = filecmp.dircmp(got, expected, ignore=[])
    assert_cmp_same(cmp)


def assert_cmp_same(cmp):
    print('assert_cmp_same', cmp.left, cmp.right)

    if cmp.left_only:
        raise AssertionError(f'Extra files frozen: {cmp.left_only}')

    if cmp.right_only:
        raise AssertionError(f'Files not frozen: {cmp.right_only}')

    if cmp.common_funny:
        raise AssertionError(f'Funny differences: {cmp.common_funny}')

    if cmp.diff_files:
        for filename in cmp.diff_files:
            path1 = Path(cmp.left) / filename
            path2 = Path(cmp.right) / filename
            assert path1.read_text() == path2.read_text()

        raise AssertionError(f'Files do not have expected content: {cmp.diff_files}')

    for subcmp in cmp.subdirs.values():
        assert_cmp_same(subcmp)


DIRS_SAME_FIXTURES = Path(__file__).parent / 'fixtures' / 'dirs_same'
DIRS_SAME_CASES = [p.name for p in DIRS_SAME_FIXTURES.iterdir()]

@pytest.mark.parametrize('dir_name', DIRS_SAME_CASES)
def test_assert_dirs_same(dir_name):
    path = DIRS_SAME_FIXTURES / dir_name

    if path.name in ('testdir', 'same'):
        assert_dirs_same(path, DIRS_SAME_FIXTURES / 'testdir')
    else:
        with pytest.raises(AssertionError):
            assert_dirs_same(path, DIRS_SAME_FIXTURES / 'testdir')
