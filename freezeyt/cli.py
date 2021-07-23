import click
import yaml

from freezeyt.freezer import freeze
from freezeyt.util import import_variable_from_module


@click.command()
@click.argument('module_name')
@click.argument('dest_path', required=False)
@click.option('--prefix', help='URL of the application root')
@click.option('--extra-page', 'extra_pages', multiple=True,
              help='Pages without any link in application')
@click.option('-c', '--config', 'config_file', type=click.File(),
              help='YAML file of configuration')
def main(module_name, dest_path, prefix, extra_pages, config_file):
    """
    MODULE_NAME
        Name of the Python web app module which will be frozen.

    DEST_PATH
        Absolute or relative path to the directory to which the files
    will be frozen.

    --prefix
        URL, where we want to deploy our static site

    --extra-page
        Path to page without any link in application

    -c / --config
        Path to configuration YAML file

    Example use:
        python -m freezeyt demo_app build --prefix 'http://localhost:8000/' --extra-page /extra/

        python -m freezeyt demo_app build -c config.yaml
    """
    if config_file != None:
        config = yaml.safe_load(config_file)
        if not isinstance(config, dict):
            raise SyntaxError(
                    f'File {config_file.name} is not a YAML dictionary.'
                    )
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

    app = import_variable_from_module(
        module_name, default_variable='app',
    )

    freeze(app, config)
