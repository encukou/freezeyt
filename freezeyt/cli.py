import click
import importlib
import yaml

from freezeyt.freezing import freeze


DEFAULT_PREFIX = 'http://localhost:8000/'


@click.command()
@click.argument('module_name')
@click.argument('dest_path')
@click.option('--prefix', default=DEFAULT_PREFIX, show_default=True, help='URL of the application root')
@click.option('--extra-page', multiple=True, help='Pages without any link in application')
@click.option('-c', '--config', default=None, type=click.File(), help='YAML file of configuration')
def main(module_name, dest_path, prefix, extra_page, config):
    """
    MODULE_NAME
        Name of the Python web app module which will be frozen.

    DEST_PATH
        Absolute or relative path to the directory to which the files
    will be frozen.

    Example use:
        python -m freezeyt demo_app build
    """
    cli_params = {
        'prefix': prefix,
        'extra_pages': list(extra_page),
        'extra_files': None,
    }

    if config:
        file_config = yaml.safe_load(config)

        if not isinstance(file_config, dict):
            raise SyntaxError(
                    f'File {config.name} is not prepared as YAML dictionary.'
                    )
        else:
            print("Loading config YAML file was successful")

            if file_config.get('prefix', None) != None:
                if prefix == DEFAULT_PREFIX:
                    cli_params['prefix'] = file_config['prefix']
                else:
                    print("WARNING: Conflicting input data in prefix!")
                    print(f"Prefix is setup to {prefix}")

            if file_config.get('extra_pages', None) != None:
                cli_params['extra_pages'].extend(file_config['extra_pages'])

            cli_params['extra_files'] = file_config.get('extra_files', None)

    module = importlib.import_module(module_name)
    app = module.app

    freeze(app, dest_path, **cli_params)
