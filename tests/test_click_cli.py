import importlib
import os
import sys
from pathlib import Path

import pytest
from yaml import safe_dump
from click.testing import CliRunner

from freezeyt.cli import main
from test_expected_output import APP_NAMES, FIXTURES_PATH, assert_dirs_same


@pytest.mark.parametrize('app_name', APP_NAMES)
def test_cli_with_fixtures_output(tmp_path, app_name):
    app_dir = Path('fixtures', app_name)
    expected = FIXTURES_PATH / app_name / 'test_expected_output'
    module_path = app_dir / 'app'
    error_path = FIXTURES_PATH / app_name / 'error.txt'
    config_file = tmp_path / 'config.yaml'
    build_dir = tmp_path / 'build'

    build_dir.mkdir()
    module_path = '.'.join(module_path.parts)

    runner = CliRunner()

    try:
        module = importlib.import_module(module_path)
        cli_args = [str(module_path), str(build_dir)]
        freeze_config = getattr(module, 'freeze_config', None)

        if freeze_config != None:
            with open(config_file, mode='w') as file:
                safe_dump(freeze_config, stream=file)

            cli_args.extend(['--config', config_file])

        if error_path.exists():
            result = runner.invoke(main, cli_args)
            assert result.exit_code != 0

        else:
            result = runner.invoke(main, cli_args)

            if not expected.exists():
                if not 'TEST_CREATE_EXPECTED_OUTPUT' in os.environ:
                    raise AssertionError(
                        f'Expected output directory ({expected}) does not exist. '
                        + '\nRun $ python -m pytest test_expected_output.py\n'
                        + 'And follow instructions'
                        )

            assert result.exit_code == 0

            assert_dirs_same(build_dir, expected)

    finally:
        sys.modules.pop('app', None)


def test_cli_with_prefix_option(tmp_path):
    module_path = Path('fixtures', 'demo_app_url_for_prefix', 'app')
    module_path = '.'.join(module_path.parts)
    expected = FIXTURES_PATH / 'demo_app_url_for_prefix' / 'test_expected_output'
    runner = CliRunner()


    try:
        module = importlib.import_module(module_path)
        freeze_config = getattr(module, 'freeze_config')
        prefix = freeze_config['prefix']
        cli_args = [str(module_path), str(tmp_path), '--prefix', prefix]

        result = runner.invoke(main, cli_args)

        if not expected.exists():
            if not 'TEST_CREATE_EXPECTED_OUTPUT' in os.environ:
                    raise AssertionError(
                        f'Expected output directory ({expected}) does not exist. '
                        + '\nRun $ python -m pytest test_expected_output.py\n'
                        + 'And follow instructions'
                        )

        assert result.exit_code == 0

        assert_dirs_same(tmp_path, expected)

    finally:
        sys.modules.pop('app', None)


def test_cli_with_extra_page_option(tmp_path):
    module_path = Path('fixtures', 'app_with_extra_page_deep', 'app')
    module_path = '.'.join(module_path.parts)
    expected = FIXTURES_PATH / 'app_with_extra_page_deep' / 'test_expected_output'
    runner = CliRunner()


    try:
        module = importlib.import_module(module_path)
        cli_args = [str(module_path), str(tmp_path)]

        freeze_config = getattr(module, 'freeze_config')

        extra_pages = []
        for extra in freeze_config['extra_pages']:
            extra_pages.append('--extra-page')
            extra_pages.append(extra)

        cli_args.extend(extra_pages)

        result = runner.invoke(main, cli_args)

        if not expected.exists():
            if not 'TEST_CREATE_EXPECTED_OUTPUT' in os.environ:
                    raise AssertionError(
                        f'Expected output directory ({expected}) does not exist. '
                        + '\nRun $ python -m pytest test_expected_output.py\n'
                        + 'And follow instructions'
                        )

        assert result.exit_code == 0

        assert_dirs_same(tmp_path, expected)

    finally:
        sys.modules.pop('app', None)


def test_cli_prefix_conflict(tmp_path):
    module_path = Path('fixtures', 'demo_app_url_for_prefix', 'app')
    module_path = '.'.join(module_path.parts)
    expected = FIXTURES_PATH / 'demo_app_url_for_prefix' / 'test_expected_output'
    config_file = tmp_path / 'config.yaml'
    build_dir = tmp_path / 'build'
    build_dir.mkdir()

    runner = CliRunner()

    try:
        module = importlib.import_module(module_path)
        freeze_config = getattr(module, 'freeze_config')
        prefix = freeze_config['prefix']
        cli_args = [str(module_path), str(build_dir), '--prefix', prefix]

        data = {'prefix': 'http://pyladies.cz/lessons/'}
        with open(config_file, mode='w') as file:
            safe_dump(data, stream=file)

        cli_args.extend(['--config', config_file])

        result = runner.invoke(main, cli_args)

        if not expected.exists():
            if not 'TEST_CREATE_EXPECTED_OUTPUT' in os.environ:
                raise AssertionError(
                    f'Expected output directory ({expected}) does not exist. '
                    + '\nRun $ python -m pytest test_expected_output.py\n'
                    + 'And follow instructions'
                    )

        assert result.exit_code == 0

        assert_dirs_same(build_dir, expected)

    finally:
        sys.modules.pop('app', None)