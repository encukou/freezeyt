import pytest

from freezeyt import freeze

from test_click_cli import run_freezeyt_cli
from fixtures.app_with_extra_files.app import app, freeze_config


def test_cli_to_files(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    app_name = 'demo_app_2pages'

    run_freezeyt_cli(['app', str(builddir)], app_name)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'second_page.html').exists()


def test_func_to_files(tmp_path):
    builddir = tmp_path / 'build'

    config = {
        **freeze_config,
        'output': {'type': 'dir', 'dir': builddir},
    }

    freeze(app, config)

    assert (builddir / 'index.html').exists()
    assert (builddir / '.nojekyll').exists()
    assert (builddir / 'CNAME').exists()
    assert (builddir / 'smile.png').exists()


@pytest.mark.parametrize('output', (
    'dict',
    {'type': 'dict'},
))
def test_func_to_dict(tmp_path, output):
    config = {**freeze_config, 'output': output}

    result = freeze(app, config)

    print(result)
    assert sorted(result) == [
        '.nojekyll', 'CNAME', 'config', 'index.html', 'smile.png',
    ]


def test_func_empty_config(tmp_path):
    config = {}

    with pytest.raises(KeyError):
        freeze(app, config)


def test_cli_to_dict_without_path(tmp_path, monkeypatch):
    config_path = tmp_path / 'freezeyt.conf'
    app_name = 'app_with_extra_files'

    config_path.write_text('output: dict')

    run_freezeyt_cli(['app', '-c', config_path], app_name)


def test_cli_to_dict_with_config_and_path(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    config_path = tmp_path / 'freezeyt.conf'
    app_name = 'app_with_extra_files'

    config_path.write_text('output: dict')

    result = run_freezeyt_cli(
        ['app', '-c', config_path, str(builddir)], app_name, check=False
    )
    assert result.exit_code != 0


def test_cli_without_path_and_output(tmp_path, monkeypatch):
    app_name = 'app_with_extra_files'

    result = run_freezeyt_cli(['app'], app_name, check=False)
    assert result.exit_code != 0
