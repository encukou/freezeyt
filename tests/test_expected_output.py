import importlib
from pathlib import Path
import filecmp

import pytest

from freezeyt import freeze


def test_output(tmp_path, module_name='demo_app'):
    module = importlib.import_module(module_name)
    app = module.app

    freeze(app, tmp_path)

    # ../test_expected_output.py
    # ../fixtures/demo_app/
    expected = Path(__file__).parent / 'fixtures' / module_name

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


def test_assert_dirs_same():
    fixture_path = Path(__file__).parent / 'fixtures' / 'dirs_same'
    for path in fixture_path.iterdir():
        print(path)
        if path.name in ('testdir', 'same'):
            assert_dirs_same(path, fixture_path / 'testdir')
        else:
            with pytest.raises(AssertionError):
                assert_dirs_same(path, fixture_path / 'testdir')
