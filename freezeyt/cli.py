import sys
import shutil

import click
import yaml

from freezeyt import freeze, MultiError
from freezeyt.util import import_variable_from_module


@click.command()
@click.argument('module_name')
@click.argument('dest_path', required=False)
@click.option('--prefix',
              help='URL where we want to deploy our static site '
                + '(the application root)')
@click.option('--extra-page', 'extra_pages', multiple=True,
              help="URLs of a page to freeze even if it's not linked from "
                + "the application. May be repeated.")
@click.option('-c', '--config', 'config_file', type=click.File(),
              help='Path to configuration YAML file')
@click.option('-C', '--import-config', 'config_var',
              help='Python variable with configuration')
@click.option('--progress', 'progress',
              type=click.Choice(['none', 'bar', 'log']),
              help='Select how to display progress')
@click.option('--cleanup/--no-cleanup', 'cleanup',
              default=None,
              help='Remove incomplete directory (if error occured). Default is to clean up.')

def main(
    module_name, dest_path, prefix, extra_pages, config_file, config_var,
    progress, cleanup,
):
    """
    MODULE_NAME
        Name of the Python web app module which will be frozen.

    DEST_PATH
        Absolute or relative path to the directory to which the files
    will be frozen.

    Example use:
        python -m freezeyt demo_app build --prefix 'http://localhost:8000/' --extra-page /extra/

        python -m freezeyt demo_app build -c config.yaml
    """
    if config_file and config_var:
        raise click.UsageError(
            "Can't pass configuration both in a file and in a variable."
        )

    elif config_file != None:
        config = yaml.safe_load(config_file)
        if not isinstance(config, dict):
            raise SyntaxError(
                    f'File {config_file.name} is not a YAML dictionary.'
                    )

    elif config_var is not None:
        config = import_variable_from_module(config_var)

    else:
        config = {}

    if extra_pages:
        config.setdefault('extra_pages', []).extend(extra_pages)

    if prefix != None:
        config['prefix'] = prefix

    if 'output' in config:
        if dest_path is not None:
            raise click.UsageError(
                'DEST_PATH argument is not needed if output is configured from file'
            )
    else:
        if dest_path is None:
            raise click.UsageError('DEST_PATH argument is required')
        config['output'] = {'type': 'dir', 'dir': dest_path}

    if progress is None:
        if sys.stdout.isatty():
            progress = 'bar'
        else:
            progress = 'log'

    if progress == 'bar':
        config.setdefault(
            'plugins', []).append('freezeyt.progressbar:ProgressBarPlugin')
    if progress in ('log', 'bar'):
        # The 'log' plugin is activated both with --progress=log and
        # --progress=bar.
        config.setdefault(
            'plugins', []).append('freezeyt.progressbar:LogPlugin')

    if cleanup is not None:
        config['cleanup'] = cleanup

    app = import_variable_from_module(
        module_name, default_variable_name='app',
    )

    try:
        freeze(app, config)
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
