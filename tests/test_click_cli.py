import importlib
import pytest
import sys

from pathlib import Path

from click.testing import CliRunner
from freezeyt.cli import main
from test_expected_output import APP_NAMES, FIXTURES_PATH, assert_dirs_same


@pytest.mark.parametrize('app_name', APP_NAMES)
def test_cli_output(tmp_path, monkeypatch, app_name):
    app_dir = Path('fixtures', app_name)
    expected = FIXTURES_PATH / app_name / 'test_expected_output'
    module_path = app_dir / 'app'
    error_path = FIXTURES_PATH / app_name / 'error.txt'
    module_path = '.'.join(module_path.parts)
    print('MOdule path:', module_path)


    # Add app_path to variable PYTHONPATH, the variable of dir that `import`
    # python looks in the variable when is started everytime
    runner = CliRunner()

    try:
        module = importlib.import_module(module_path)
        print('MODULE:', module)
        cli_args = [str(module_path), str(tmp_path)]

        for arg_name in 'prefix', 'extra_pages':
            arg_value = getattr(module, arg_name, None)
            if arg_value != None:
                if arg_name == 'prefix':
                    cli_args.extend(['--prefix', arg_value])
                elif arg_name == 'extra_pages':
                    for page in arg_value:
                        cli_args.extend(['--extra-page', page])
                else:
                    cli_args.append(arg_value)

        print('CLI ARGS:', cli_args)

        if error_path.exists():
            # with pytest.raises(ValueError):
            # nevyvolava chybu
            result = runner.invoke(main, cli_args)
            print('Result output:', result.output)
            raise AssertionError

        else:
            result = runner.invoke(main, cli_args)
            print('Result output:', result.output)

            if not expected.exists():
                raise AssertionError(
                    f'Expected output directory ({expected}) does not exist. '
                    + '\nRun $ python -m pytest test_expected_output.py\n'
                    + 'And follow instructions'
                    )

            assert result.exit_code == 0
            assert_dirs_same(tmp_path, expected)
    finally:
        sys.modules.pop('app', None)
