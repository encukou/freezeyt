from click.testing import CliRunner
from freezeyt import cli
from test_expected_output import APP_NAMES, FIXTURES_PATH, assert_dirs_same



@pytest.mark.parametrize('app_name', APP_NAMES)
def test_cli_output(tmp_path, monkeypatch, app_name):
    runner = CliRunner()
    app_path = FIXTURES_PATH / app_name
    error_path = app_path / 'error.txt'

    # I dont know how to handle this convert
    app = "path/to/app as path.to.module"

    cli_args = [app, tmp_path]

    for arg_name in 'prefix', 'extra_pages':
        arg_value = getattr(module, arg_name, None)
        if arg_value != None:
            if arg_name == 'extra_pages':
                make_cli_arg = lambda s: f"--extra-page {s}"
                extra_pages = list(map(make_cli_arg, arg_value))
                cli_args.extend(extra_pages)
            else:
                cli_args.append = arg_value


    expected = app_path / 'test_expected_output'

    if error_path.exists():
        with pytest.raises(ValueError):
            runner.invoke(cli, cli_args)
    else:
        runner.invoke(cli, cli_args)

        if not expected.exists():
            raise AssertionError(
                f'Expected output directory ({expected}) does not exist. '
                + '\nRun $ python -m pytest test_expected_output.py\n'
                + 'And follow instructions'

                )

        assert_dirs_same(tmp_path, expected)