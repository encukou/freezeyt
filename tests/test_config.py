import pathlib

import pytest

from freezeyt import freeze, ExternalURLError, Config

from test_click_cli import run_freezeyt_cli
from fixtures.app_with_extra_files.app import app, freeze_config
from testutil import context_for_test, assert_dirs_same, FIXTURES_PATH


def test_cli_to_files(tmp_path):
    builddir = tmp_path / 'build'
    app_name = 'app_2pages'

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
    assert (builddir / 'bin_range.dat').exists()
    assert (builddir / 'smile2.png').exists()


def test_func_to_dict(tmp_path):
    config = {**freeze_config, 'output': {'type': 'dict'}}

    result = freeze(app, config)

    print(result)
    assert sorted(result) == [
        '.nojekyll', 'CNAME', 'bin_range.dat', 'config',
        'index.html', 'smile.png', 'smile2.png'
    ]


def test_func_empty_config(tmp_path):
    config: Config = {}

    with pytest.raises(KeyError):
        freeze(app, config)


def test_cli_to_dict_without_path(tmp_path, monkeypatch):
    config_path = tmp_path / 'freezeyt.conf'
    app_name = 'app_with_extra_files'

    config_path.write_text('output: {type: dict}')

    run_freezeyt_cli(['app', '-c', config_path], app_name)


def test_cli_to_dict_with_config_and_path(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    config_path = tmp_path / 'freezeyt.conf'
    app_name = 'app_with_extra_files'

    config_path.write_text('output: {type: dict}')

    result = run_freezeyt_cli(
        ['app', '-c', config_path, str(builddir)], app_name, check=False
    )
    assert result.exit_code != 0


def test_cli_without_path_and_output(tmp_path, monkeypatch):
    app_name = 'app_with_extra_files'

    result = run_freezeyt_cli(['app'], app_name, check=False)
    assert result.exit_code != 0


def test_simple_output_specification(tmp_path):
    expected = FIXTURES_PATH / 'app_2pages' / 'test_expected_output'

    with context_for_test('app_2pages') as module:
        freeze_config = {'output': str(tmp_path)}

        freeze(module.app, freeze_config)

        assert_dirs_same(tmp_path, expected)


def test_invalid_output_type(tmp_path):
    with context_for_test('app_2pages') as module:
        freeze_config = {'output': {'type': 'bad output type'}}

        with pytest.raises(ValueError):
            freeze(module.app, freeze_config)


def test_no_output_dir(tmp_path):
    with context_for_test('app_2pages') as module:
        freeze_config = {'output': {'type': 'dir'}}

        with pytest.raises(ValueError):
            freeze(module.app, freeze_config)


def test_external_extra_files(tmp_path):
    with context_for_test('app_2pages') as module:
        freeze_config = {
            'output': {'type': 'dict'},
            'extra_pages': ['http://external.example/foo.html'],
        }

        with pytest.raises(ExternalURLError):
            freeze(module.app, freeze_config)


def test_external_extra_files_generator(tmp_path):
    def gen(app):
        yield 'http://external.example/foo.html'
    with context_for_test('app_2pages') as module:
        freeze_config = {
            'output': {'type': 'dict'},
            'extra_pages': [gen],
        }

        with pytest.raises(ExternalURLError):
            freeze(module.app, freeze_config)

def my_url_to_path(path):
    return {
        '': 'new-index.html',
        'users/': 'users/new-index.html',
        'users/a/': pathlib.PurePosixPath('users', 'a-user'),
        'users/b/': 'b-user/index-page',
    }[path]

@pytest.mark.parametrize('function_spec', [
    f'{__name__}:my_url_to_path',  # "module:name" string
    my_url_to_path, # Python function
])
def test_url_to_path(function_spec):

    with context_for_test('app_structured') as module:
        config = {
            'output': {'type': 'dict'},
            'url_to_path': function_spec,
        }

        result = freeze(module.app, config)

    expected = {
        'new-index.html': module.expected_dict['index.html'],
        'users': {
            'new-index.html': module.expected_dict['users']['index.html'],
            'a-user': module.expected_dict['users']['a']['index.html'],
        },
        'b-user': {
            'index-page': module.expected_dict['users']['b']['index.html'],
        },
    }

    assert result == expected
