import sys
import importlib

from freezeyt.freezing import freeze


def main():
    app_module_name = sys.argv[1]

    module = importlib.import_module(app_module_name)
    app = module.app

    path = sys.argv[2]
    freeze(app, path)
