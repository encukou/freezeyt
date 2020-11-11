import click
import importlib
import yaml

from freezeyt.freezing import freeze


@click.command()
@click.argument('module_name')
@click.argument('dest_path')
@click.option('--prefix', default='http://localhost:8000/', help='URL of the application root')
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
    if config != None:
        config_cont = yaml.safe_load(config)
        if not isinstance(config_cont, dict):
            raise SyntaxError(f'File {config.name} is not made in a YAML convence')
        else:
            print("Load configuration was succesful")
    else:
        config_cont = None


    module = importlib.import_module(module_name)
    app = module.app

    freeze(app, dest_path, prefix=prefix, extra_pages=extra_page, config=config_cont)
