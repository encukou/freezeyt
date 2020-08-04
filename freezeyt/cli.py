import importlib

import click

from freezeyt.freezing import freeze


@click.command()
@click.argument('module_name')
@click.argument('dest_path')
def main(module_name, dest_path):
    module = importlib.import_module(module_name)
    app = module.app

    freeze(app, dest_path)
