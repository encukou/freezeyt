"""Command-Line Interface for freezeyt"""

import sys
import shutil
from typing import Optional, TextIO, BinaryIO, List
try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    # Python 3.10 and below
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

import click
import yaml

from freezeyt import freeze, MultiError
from freezeyt.util import import_variable_from_module
from freezeyt.compat import Literal

# Use -h as an alias for --help
# (see https://click.palletsprojects.com/en/stable/documentation/#help-parameter-customization)
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app', required=False)
@click.argument('dest_path', required=False, type=click.Path(file_okay=False))
@click.option('-o', '--output', type=click.Path(file_okay=False),
              help='Absolute or relative path to the output directory')
@click.option('--prefix',
              help='URL where we want to deploy our static site '
                + '(the application root)')
@click.option('--extra-page', 'extra_pages', multiple=True,
              help="URLs of a page to freeze even if it's not linked from "
                + "the application. May be repeated.")
@click.option('-t', '--toml-config', 'toml_config_file', type=click.File('rb'),
              help='Path to configuration TOML file')
@click.option('-y', '--yaml-config', '-c', '--config', 'yaml_config_file',
              type=click.File(),
              help='Path to configuration YAML file')
@click.option('-C', '--import-config', 'config_var',
              help='Python variable with configuration')
@click.option('--progress', 'progress',
              type=click.Choice(['none', 'bar', 'log']),
              help='Select how to display progress')
@click.option('--cleanup/--no-cleanup', 'cleanup',
              default=None,
              help='Remove incomplete directory (if error occured). Default is to clean up.')
@click.option('--gh-pages/--no-gh-pages', 'gh_pages',
              default=None,
              help='If activated and freeze was successful, create git gh-pages branch in output folder and commit all files to that branch.')
@click.option('-x', '--fail-fast/--no-fail-fast',
              default=None,
              help='Stop on the first error')
def main(
    app: str,
    dest_path: str,
    output: Optional[str],
    prefix: Optional[str],
    extra_pages: Optional[List[str]],
    toml_config_file: Optional[BinaryIO],
    yaml_config_file: Optional[TextIO],
    config_var: Optional[str],
    progress: Optional[Literal['none', 'bar', 'log']],
    cleanup: Optional[bool],
    gh_pages: Optional[str],
    fail_fast: Optional[bool],
) -> None:
    """
    APP
        Name of the Python web app module which will be frozen.

    DEST_PATH
        Absolute or relative path to the directory to which the files
    will be frozen.

    Example use:
        python -m freezeyt demo_app build --prefix 'http://localhost:8000/' --extra-page /extra/

        python -m freezeyt demo_app build -c config.yaml
    """

    config_options = [toml_config_file, yaml_config_file, config_var]
    if len([c for c in config_options if c is not None]) > 1:
        raise click.UsageError(
            "Can only specify one of: --toml-config (-t), "
            + "--yaml-config (-y, -c), -import-config (-C)"
        )
    elif toml_config_file is not None:
        config = tomllib.load(toml_config_file)
        assert isinstance(config, dict)
    elif yaml_config_file is not None:
        config = yaml.safe_load(yaml_config_file)
        if not isinstance(config, dict):
            raise SyntaxError(
                    f'File {yaml_config_file.name} is not a YAML dictionary.'
                )
    elif config_var is not None:
        config = import_variable_from_module(config_var)

    else:
        config = {}

    if app is not None:
        config['app'] = app
    if config.get('app') is None:
        raise click.UsageError('APP argument or "app" in config is required')

    if dest_path and output:
        raise click.UsageError('Specify only DEST_PATH argument or --output')
    if dest_path is None:
        dest_path = output
    if dest_path is not None:
        config['output'] = dest_path
    if config.get('output') is None:
        raise click.UsageError('DEST_PATH, --output, or "output" in config is required')

    if prefix != None:
        config['prefix'] = prefix

    if extra_pages:
        config.setdefault('extra_pages', []).extend(extra_pages)

    if progress is None:
        if sys.stdout.isatty():
            progress = 'bar'
        else:
            progress = 'log'

    if progress == 'bar':
        config.setdefault(
            'plugins', []).append('freezeyt.plugins:ProgressBarPlugin')
    if progress in ('log', 'bar'):
        # The 'log' plugin is activated both with --progress=log and
        # --progress=bar.
        config.setdefault(
            'plugins', []).append('freezeyt.plugins:LogPlugin')

    if cleanup is not None:
        config['cleanup'] = cleanup

    if gh_pages is not None:
        config['gh_pages'] = gh_pages

    if fail_fast is not None:
        config['fail_fast'] = fail_fast

    try:
        freeze(app=None, config=config)
    except MultiError as multierr:
        if sys.stderr.isatty():
            cols, lines = shutil.get_terminal_size()
            message = f' {multierr} '
            click.echo(file=sys.stderr)
            click.secho(message.center(cols, '='), file=sys.stderr, fg='red')
        for task in multierr.tasks:
            message = str(task.exception)
            if message:
                # Separate the error type and value by a semicolon
                # (only if there is a value)
                message = ': ' + message
            err_type = click.style(type(task.exception).__name__, fg='red')
            path = click.style(task.path, fg='cyan')
            click.echo(f'{err_type}{message}', file=sys.stderr)
            click.echo(f'  in {path}', file=sys.stderr)
            for reason in task.reasons:
                click.echo(f'    {reason}', file=sys.stderr)
        exit(1)
