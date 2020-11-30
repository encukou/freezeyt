import importlib
import os
import sys
from pathlib import Path
from contextlib import contextmanager

import pytest
from yaml import safe_dump
from click.testing import CliRunner

from freezeyt.cli import main
from test_expected_output import APP_NAMES, FIXTURES_PATH, assert_dirs_same


def run_and_check(cli_args, app_name, build_dir):
    app_dir = FIXTURES_PATH / app_name
    error_path = FIXTURES_PATH / app_name / 'error.txt'
    expected = FIXTURES_PATH / app_name / 'test_expected_output'

    build_dir.mkdir()

    runner = CliRunner(env={'PYTHONPATH': str(app_dir)})

    result = runner.invoke(main, cli_args)
    if error_path.exists():
        assert result.exit_code != 0

    else:
        if not expected.exists():
            if 'TEST_CREATE_EXPECTED_OUTPUT' in os.environ:
                pytest.skip('Expected output is created in other tests')
            else:
                raise AssertionError(
                    f'Expected output directory ({expected}) does not exist. '
                    + 'Run with TEST_CREATE_EXPECTED_OUTPUT=1 to create it'
                )
        else:
            assert result.exit_code == 0

            assert_dirs_same(build_dir, expected)


@contextmanager
def context_for_test(app_name, monkeypatch):
    app_dir = FIXTURES_PATH / app_name
    monkeypatch.syspath_prepend(app_dir)
    try:
        module = importlib.import_module('app')
        yield module
    finally:
        sys.modules.pop('app', None)


@pytest.mark.parametrize('app_name', APP_NAMES)
def test_cli_with_fixtures_output(tmp_path, app_name, monkeypatch):
    app_dir = FIXTURES_PATH / app_name
    config_file = tmp_path / 'config.yaml'
    build_dir = tmp_path / 'build'

    with context_for_test(app_name, monkeypatch) as module:
        cli_args = ['app', str(build_dir)]
        freeze_config = getattr(module, 'freeze_config', None)

        if freeze_config != None:
            with open(config_file, mode='w') as file:
                safe_dump(freeze_config, stream=file)

            cli_args.extend(['--config', config_file])

        run_and_check(cli_args, app_name, build_dir)


def test_cli_with_prefix_option(tmp_path, monkeypatch):
    app_name = 'demo_app_url_for_prefix'
    app_dir = FIXTURES_PATH / app_name
    build_dir = tmp_path / 'build'

    with context_for_test(app_name, monkeypatch) as module:
        freeze_config = getattr(module, 'freeze_config')
        prefix = freeze_config['prefix']
        cli_args = ['app', str(build_dir), '--prefix', prefix]

        run_and_check(cli_args, app_name, build_dir)


def test_cli_with_extra_page_option(tmp_path, monkeypatch):
    app_name = 'app_with_extra_page_deep'
    app_dir = FIXTURES_PATH / app_name
    build_dir = tmp_path / 'build'

    with context_for_test(app_name, monkeypatch) as module:
        cli_args = ['app', str(build_dir)]

        freeze_config = getattr(module, 'freeze_config')

        extra_pages = []
        for extra in freeze_config['extra_pages']:
            extra_pages.append('--extra-page')
            extra_pages.append(extra)

        cli_args.extend(extra_pages)

        run_and_check(cli_args, app_name, build_dir)


def test_cli_prefix_conflict(tmp_path, monkeypatch):
    app_name = 'demo_app_url_for_prefix'
    app_dir = FIXTURES_PATH / app_name
    config_file = tmp_path / 'config.yaml'
    build_dir = tmp_path / 'build'

    with context_for_test(app_name, monkeypatch) as module:
        freeze_config = getattr(module, 'freeze_config')
        prefix = freeze_config['prefix']
        cli_args = ['app', str(build_dir), '--prefix', prefix]

        data = {'prefix': 'http://pyladies.cz/lessons/'}
        with open(config_file, mode='w') as file:
            safe_dump(data, stream=file)

        cli_args.extend(['--config', config_file])

        run_and_check(cli_args, app_name, build_dir)
