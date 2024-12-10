import os
import shutil
import traceback

import pytest

from freezeyt import freeze, InfiniteRedirection, MultiError, UnexpectedStatus
from testutil import FIXTURES_PATH, APP_NAMES, context_for_test
from testutil import assert_dirs_same, raises_multierror_with_one_exception


@pytest.mark.parametrize('app_name', APP_NAMES)
def test_output(tmp_path, monkeypatch, app_name):
    app_path = FIXTURES_PATH / app_name
    error_path = app_path / 'error.txt'

    with context_for_test(app_name) as module:
        app = module.app

        freeze_config = getattr(module, 'freeze_config', {})
        expected_dict = getattr(module, 'expected_dict', None)
        expecting_dir = not getattr(module, 'no_expected_directory', False)

        freeze_config['output'] = {'type': 'dir', 'dir': tmp_path}

        if error_path.exists():
            expected_error_info = error_path.read_text().strip()
            with pytest.raises((ValueError, MultiError)) as excinfo:
                freeze(app, freeze_config)
            if isinstance(excinfo.value, MultiError):
                # Expected error info looks like:
                # ```
                # MultiError:
                #     UnexpectedStatus
                #     SomeOtherException
                # ```
                multierror = excinfo.value
                error_info = "MultiError:\n" + '\n'.join(sorted(
                    ' ' * 4 + type(exc).__name__
                    for exc in multierror.exceptions
                ))
                for exc in multierror.exceptions:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)
                assert error_info == expected_error_info
            else:
                print(excinfo.getrepr(style='short'))
                exception_name = excinfo.typename
                assert exception_name == expected_error_info
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
        freeze_config['status_handlers'] = {'3xx': 'follow'}

        result = freeze(module.app, freeze_config) # freeze content to dict

        assert result == module.expected_dict_follow


def test_redirect_policy_ignore(tmp_path, monkeypatch):
    with context_for_test('app_redirects') as module:
        freeze_config = module.freeze_config

        freeze_config['output'] = {'type': 'dict'}
        freeze_config['status_handlers'] = {'3xx': 'ignore'}

        result = freeze(module.app, freeze_config) # freeze content to dict

        assert result == module.expected_dict_ignore


def test_circular_redirect(tmp_path, monkeypatch):
    with context_for_test('circular_redirect') as module:
        freeze_config = module.freeze_config

        freeze_config['output'] = {'type': 'dir', 'dir': tmp_path}
        freeze_config['status_handlers'] = {'3xx': 'follow'}

        with raises_multierror_with_one_exception(InfiniteRedirection):
            freeze(module.app, freeze_config)


def test_multierror(tmp_path, monkeypatch):
    with context_for_test('app_2_broken_links') as module:
        freeze_config = {
            'output': {'type': 'dir', 'dir': tmp_path},
        }

        with pytest.raises(MultiError) as excinfo:
            freeze(module.app, freeze_config)

        multierror = excinfo.value
        assert len(multierror.exceptions) == 2
        for exception in multierror.exceptions:
            with pytest.raises(UnexpectedStatus):
                raise exception
