from freezeyt import freeze

from test_click_cli import run_freezeyt_cli, context_for_test


def test_cli_to_files(tmp_path, monkeypatch):
    builddir = tmp_path / 'build'
    app_name = 'demo_app_2pages'

    with context_for_test(app_name, monkeypatch):
        run_freezeyt_cli(['app', str(builddir)], app_name)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'second_page.html').exists()


def test_func_to_files(tmp_path):
    builddir = tmp_path / 'build'

    from tests.fixtures.demo_app_2pages.app import app

    config = {
        'output': {'type': 'dir', 'dir': builddir},
    }

    freeze(app, builddir, config)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'second_page.html').exists()


def test_func_to_dict(tmp_path):
    builddir = tmp_path / 'build'

    from tests.fixtures.demo_app_2pages.app import app

    config = {
        'output': 'dict',
    }

    result = freeze(app, builddir, config)

    assert sorted(result) == ['index.html', 'second_page.html']
