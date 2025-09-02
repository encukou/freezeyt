from textwrap import dedent

import pytest
from yaml import safe_dump
from click.testing import CliRunner

from freezeyt.cli import main
from testutil import FIXTURES_PATH, context_for_test, assert_dirs_same

APP_NAMES = [
    p.name
    for p in FIXTURES_PATH.iterdir()
    if (p / 'app.py').exists() and (p / 'test_expected_output').exists()
]


def run_freezeyt_cli(cli_args, app_name, check=True):
    app_dir = FIXTURES_PATH / app_name

    runner = CliRunner(env={'PYTHONPATH': str(app_dir)})

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.syspath_prepend(app_dir)
        result = runner.invoke(main, cli_args)

    print(result.output)

    if check:
        if result.exception is not None:
            raise result.exception
        assert result.exit_code == 0

    return result


def run_and_check(cli_args, app_name, build_dir):
    error_path = FIXTURES_PATH / app_name / 'error.txt'
    expected = FIXTURES_PATH / app_name / 'test_expected_output'

    result = run_freezeyt_cli(cli_args, app_name, check=False)

    if error_path.exists():
        assert result.exit_code != 0

    else:
        if result.exception is not None:
            raise result.exception
        assert result.exit_code == 0

        assert_dirs_same(build_dir, expected)


@pytest.mark.parametrize('app_name', APP_NAMES)
def test_cli_with_fixtures_output(tmp_path, app_name):
    config_file = tmp_path / 'config.yaml'
    build_dir = tmp_path / 'build'
    cli_args = ['app', str(build_dir)]

    with context_for_test(app_name) as module:
        freeze_config = getattr(module, 'freeze_config', None)

        if not getattr(module, 'config_is_serializable', True):
            pytest.skip('Config is not serializable')

    if freeze_config != None:
        with open(config_file, mode='w') as file:
            safe_dump(freeze_config, stream=file)

        cli_args.extend(['--config', config_file])

    run_and_check(cli_args, app_name, build_dir)


def test_cli_with_prefix_option(tmp_path):
    app_name = 'app_url_for_prefix'
    build_dir = tmp_path / 'build'
    cli_args = ['app', str(build_dir)]

    with context_for_test(app_name) as module:
        freeze_config = getattr(module, 'freeze_config')
        prefix = freeze_config['prefix']

    cli_args.extend(['--prefix', prefix])

    run_and_check(cli_args, app_name, build_dir)


def test_cli_with_config_variable(tmp_path):
    app_name = 'app_with_extra_files'
    build_dir = tmp_path / 'build'
    cli_args = ['app', str(build_dir), '--import-config', 'app:freeze_config']

    with context_for_test(app_name):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_with_extra_page_option(tmp_path):
    app_name = 'app_with_extra_page_deep'
    build_dir = tmp_path / 'build'
    cli_args = ['app', str(build_dir)]

    with context_for_test(app_name) as module:
        freeze_config = getattr(module, 'freeze_config')

    for extra_page in freeze_config['extra_pages']:
        cli_args.extend(['--extra-page', extra_page])

    run_and_check(cli_args, app_name, build_dir)


def test_cli_prefix_overrides_config(tmp_path):
    app_name = 'app_url_for_prefix'
    build_dir = tmp_path / 'build'
    config_file = tmp_path / 'config.yaml'
    config_content = {'prefix': 'http://pyladies.cz/lessons/'}
    with open(config_file, mode='w') as file:
        safe_dump(config_content, stream=file)
    cli_args = ['app', str(build_dir)]

    with context_for_test(app_name) as module:
        freeze_config = getattr(module, 'freeze_config')
        prefix = freeze_config['prefix']

    cli_args.extend(['--prefix', prefix, '--config', config_file])

    run_and_check(cli_args, app_name, build_dir)


def test_cli_nonstandard_app_name(tmp_path):
    app_name = 'app_nonstandard_name'
    build_dir = tmp_path / 'build'
    cli_args = ['application:wsgi_application', str(build_dir)]

    with context_for_test(app_name, module_name='application'):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_nonstandard_dotted_app_name(tmp_path):
    app_name = 'app_nonstandard_name'
    build_dir = tmp_path / 'build'
    cli_args = ['application:obj.app', str(build_dir)]

    with context_for_test(app_name, module_name='application'):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_cleanup_config_works(tmp_path):
    app_name = 'app_cleanup_config'
    build_dir = tmp_path / 'build'
    cli_args = [
        'app', str(build_dir), '--import-config', 'app:freeze_config'
    ]

    with context_for_test(app_name):
        run_and_check(cli_args, app_name, build_dir)
    assert build_dir.exists()
    assert (build_dir / 'index.html').exists()


def test_cli_cleanup_command_line_has_higher_priority(tmp_path):
    app_name = 'app_cleanup_config'
    build_dir = tmp_path / 'build'
    cli_args = [
        'app', str(build_dir),
        '--cleanup',
        '--import-config',
        'app:freeze_config'
    ]
    with context_for_test(app_name):
        run_and_check(cli_args, app_name, build_dir)
    assert not build_dir.exists()


def test_cli_gh_pages_command_line_has_higher_priority(tmp_path):
    app_name = 'app_2pages'
    output_dir = tmp_path / 'output_dir'
    (tmp_path / "gh_pages_true.yaml").write_text("gh_pages: True")
    cli_args = [
        'app', str(output_dir),
        '--no-gh-pages', # disable gh_pages in CLI
        '--config',
        f'{str(tmp_path / "gh_pages_true.yaml")}',
    ]
    with context_for_test(app_name):
        run_and_check(cli_args, app_name, output_dir)
    assert not (output_dir / ".git").exists() # the .git directory has not to exist
    assert not (output_dir / "CNAME").exists() # the CNAME file has not to exist
    assert not (output_dir / ".nojekyll").exists() # the .nojekyll has not to exist


def test_cli_app_argument_overrides_config(tmp_path):
    app_name = 'app_simple'
    build_dir = tmp_path / 'build'
    config_file = tmp_path / 'config.yaml'
    config_content = {'app': 'app_nonexisting'}
    with open(config_file, mode='w') as file:
        safe_dump(config_content, stream=file)
    cli_args = ['app', str(build_dir), '--config', config_file]

    run_and_check(cli_args, app_name, build_dir)


def test_cli_dest_path_overrides_config(tmp_path):
    app_name = 'app_simple'
    build_dir_conf = tmp_path / 'build_conf'
    build_dir_cli = tmp_path / 'build_cli'
    config_file = tmp_path / 'config.yaml'
    config_content = {'output': {'type': 'dir', 'dir': str(build_dir_conf)}}
    with open(config_file, mode='w') as file:
        safe_dump(config_content, stream=file)
    cli_args = ['app', str(build_dir_cli), '--config', config_file]

    run_and_check(cli_args, app_name, build_dir_cli)
    assert not build_dir_conf.exists()


def test_cli_app_as_argument_no_dest_path(tmp_path):
    app_name = 'app_simple'
    build_dir = tmp_path / 'build'
    cli_args = ['app']

    with pytest.raises(SystemExit):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_output_argument_with_option(tmp_path):
    app_name = 'app_simple'
    build_dir_1 = tmp_path / 'build_1'
    build_dir_2 = tmp_path / 'build_2'

    cli_args = ['app', str(build_dir_1), '-o', str(build_dir_2)]
    with pytest.raises(SystemExit):
        run_and_check(cli_args, app_name, build_dir_1)


def test_cli_dest_path_as_argument_no_app(tmp_path):
    """Error: missing output which is required"""
    app_name = 'app_simple'
    build_dir = tmp_path / 'build'
    cli_args = [str(build_dir)]

    with pytest.raises(SystemExit):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_app_from_config_file(tmp_path):
    app_name = 'app_simple'
    build_dir = tmp_path / 'build'
    config_file = tmp_path / 'config.yaml'
    config_content = {'app': 'app'}
    with open(config_file, mode='w') as file:
        safe_dump(config_content, stream=file)
    cli_args = ['-o', str(build_dir), '--config', config_file]

    with context_for_test(app_name):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_dest_path_from_config_file(tmp_path):
    app_name = 'app_simple'
    build_dir = tmp_path / 'build'
    config_file = tmp_path / 'config.yaml'
    config_content = {'output': {'type': 'dir', 'dir': str(build_dir)}}
    with open(config_file, mode='w') as file:
        safe_dump(config_content, stream=file)
    cli_args = ['app', '--config', config_file]

    with context_for_test(app_name):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_dest_path_and_app_from_config_file(tmp_path):
    app_name = 'app_simple'
    build_dir = tmp_path / 'build'
    config_file = tmp_path / 'config.yaml'
    config_content = {
        'app': 'app',
        'output': {'type': 'dir', 'dir': str(build_dir)}
    }
    with open(config_file, mode='w') as file:
        safe_dump(config_content, stream=file)
    cli_args = ['--config', config_file]

    with context_for_test(app_name):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_app_as_str_from_config_variable(tmp_path):
    app_name = 'app_with_config_variable'
    build_dir = tmp_path / 'build'
    cli_args = ['-o', str(build_dir), '--import-config', 'application:freeze_config_str']

    with context_for_test(app_name, module_name='application'):
        run_and_check(cli_args, app_name, build_dir)


def test_cli_app_as_object_from_config_variable(tmp_path):
    app_name = 'app_with_config_variable'
    build_dir = tmp_path / 'build'
    cli_args = ['-o', str(build_dir), '--import-config', 'application:freeze_config_object']

    with context_for_test(app_name, module_name='application'):
        run_and_check(cli_args, app_name, build_dir)

def test_cli_fail_fast_option(tmp_path):
    app_name = 'app_fail_fast'
    build_dir = tmp_path / 'build'
    cli_args = ['app', str(build_dir), '-x']

    with context_for_test(app_name):
        # We expect a TestFailFastError, but use ValueError
        # (a superclass) so we don't need to import
        # TestFailFastError itself.
        with pytest.raises(ValueError):
            run_freezeyt_cli(cli_args, app_name)


def test_cli_fail_fast_option_priority_disable(tmp_path):
    """
    Test CLI option --no-fail-fast overwrite freezeyt config 'fail_fast with value True'
    """
    app_name = 'app_fail_fast'
    build_dir = tmp_path / 'build'
    cli_args = [
        'app', str(build_dir), '--no-fail-fast', '--import-config', 'app:freeze_config'
    ]

    with context_for_test(app_name):
        # If program finish with exit code 1, that means it ended with MultiError
        run_and_check(cli_args, app_name, build_dir)


def test_cli_fail_fast_option_priority_enable(tmp_path):
    """
    Test CLI option -x overwrite freezeyt config 'fail_fast' with value False
    """
    app_name = 'app_fail_fast'
    build_dir = tmp_path / 'build'
    config_file = tmp_path / 'config.yaml'
    config_content = {
        'fail_fast': False
    }
    with open(config_file, mode='w') as file:
        safe_dump(config_content, stream=file)

    cli_args = [
        'app', str(build_dir), '-x', '--config', config_file
    ]

    with context_for_test(app_name):
        with pytest.raises(ValueError):
            run_freezeyt_cli(cli_args, app_name)

def test_help():
    """Test that -h does the same as --help: show the help."""
    runner = CliRunner()
    result_help = runner.invoke(main, ['--help'])
    result_h = runner.invoke(main, ['-h'])

    assert result_help.output == result_h.output
    assert result_help.exit_code == result_h.exit_code == 0

    assert 'Usage:' in result_help.stdout


def test_multierror_output_redirect(tmp_path):
    app_name = 'broken_redirects'
    build_dir = tmp_path / 'build'
    with context_for_test(app_name):
        result = run_freezeyt_cli(
            ['app', str(build_dir)], app_name, check=False,
        )
    assert result.output.strip().endswith("linked from: index.html")
    for message in (
        """
        UnexpectedStatus: 302 FOUND (-> /to-self/)
          in to-self/index.html
            linked from: index.html
        """,
        """
        UnexpectedStatus: 302 FOUND (-> nonexistent.wtf)
          in to-nonexistent/index.html
            linked from: index.html
        """,
        """
        UnexpectedStatus: 302 FOUND (-> https://nowhere.invalid)
          in to-external/index.html
            linked from: index.html
        """,
        """
        UnexpectedStatus: 302 FOUND (-> /circular2/)
          in circular/index.html
            linked from: index.html
        """,
        """
        UnexpectedStatus: 301 MOVED PERMANENTLY
          in without-location/index.html
            linked from: index.html
        """,
    ):
        assert dedent(message).strip() in result.output
