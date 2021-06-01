import importlib
import os
import shutil

import pytest

from freezeyt import freeze, InfiniteRedirection
from testutil import FIXTURES_PATH, context_for_test, assert_dirs_same


APP_NAMES = [
    p.name
    for p in FIXTURES_PATH.iterdir()
    if (p / 'app.py').exists()
]

@pytest.mark.parametrize('app_name', APP_NAMES)
def test_output(tmp_path, monkeypatch, app_name):
    app_path = FIXTURES_PATH / app_name
    error_path = app_path / 'error.txt'

    with context_for_test(app_name) as module:
        module = importlib.import_module('app')
        app = module.app

        freeze_config = getattr(module, 'freeze_config', {})
        expected_dict = getattr(module, 'expected_dict', None)
        expecting_dir = not getattr(module, 'no_expected_directory', False)

        freeze_config['output'] = {'type': 'dir', 'dir': tmp_path}

        if error_path.exists():
            with pytest.raises(ValueError):
                freeze(app, freeze_config)
        else:
            # Non error app.

            # We want to check against expected data stored in a directory
            # and/or in a dict. At least one of those must exist.
            if not expecting_dir and expected_dict is None:
                raise AssertionError(
                    f'({app_name}) is not contain any'
                    + 'expected output (dict or dir)'
                )

            if expecting_dir:
                # test the output saved in dir 'test_expected_output'
                freeze(app, freeze_config) # freeze content to tmp_path
                expected = app_path / 'test_expected_output'

                if not expected.exists():
                    make_output = os.environ.get('TEST_CREATE_EXPECTED_OUTPUT')
                    if make_output == '1':
                        shutil.copytree(tmp_path, expected)
                    else:
                        raise AssertionError(
                            f'Expected output directory ({expected}) does not exist. '
                            + 'Run with TEST_CREATE_EXPECTED_OUTPUT=1 to create it'
                        )

                assert_dirs_same(tmp_path, expected)

            if expected_dict is not None:
                # test the output saved in dictionary
                freeze_config['output'] = {'type': 'dict'}

                result = freeze(app, freeze_config) # freeze content to dict

                assert result == expected_dict


def test_redirect_policy_follow(tmp_path, monkeypatch):
    with context_for_test('app_redirects') as module:
        freeze_config = module.freeze_config

        freeze_config['output'] = {'type': 'dict'}
        freeze_config['redirect_policy'] = 'follow'

        result = freeze(module.app, freeze_config) # freeze content to dict

        assert result == module.expected_dict_follow


def test_circular_redirect(tmp_path, monkeypatch):
    with context_for_test('circular_redirect') as module:
        freeze_config = module.freeze_config

        freeze_config['output'] = {'type': 'dir', 'dir': tmp_path}
        freeze_config['redirect_policy'] = 'follow'

        with pytest.raises(InfiniteRedirection):
            freeze(module.app, freeze_config)
