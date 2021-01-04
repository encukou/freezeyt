import pytest

from freezeyt import freeze

from test_click_cli import run_freezeyt_cli
from fixtures.demo_app_2pages.app import app


def test_cli_to_files(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    app_name = 'demo_app_2pages'

    run_freezeyt_cli(['app', str(builddir)], app_name)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'second_page.html').exists()


def test_func_to_files(tmp_path):
    builddir = tmp_path / 'build'

    config = {
        'output': {'type': 'dir', 'dir': builddir},
    }

    freeze(app, builddir, config)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'second_page.html').exists()


@pytest.mark.parametrize('config', (
    {'output': 'dict'},
    {'output': {'type': 'dict'}},
))
def test_func_to_dict(tmp_path, config):
    builddir = tmp_path / 'build'

    result = freeze(app, builddir, config)

    assert sorted(result) == ['index.html', 'second_page.html']


def test_cli_to_dict_without_path(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    config_path = tmp_path / 'freezeyt.conf'
    app_name = 'demo_app_2pages'

    config_path.write_text('output: dict')

    run_freezeyt_cli(['app', '-c', config_path], app_name)


def test_cli_to_dict_with_config_and_path(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    config_path = tmp_path / 'freezeyt.conf'
    app_name = 'demo_app_2pages'

    config_path.write_text('output: dict')

    result = run_freezeyt_cli(
        ['app', '-c', config_path, str(builddir)], app_name, check=False
    )
    assert result.exit_code != 0


def test_cli_without_path_and_output(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    app_name = 'demo_app_2pages'

    result = run_freezeyt_cli(['app'], app_name, check=False)
    assert result.exit_code != 0
