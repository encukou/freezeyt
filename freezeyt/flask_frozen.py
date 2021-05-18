from pathlib import Path
from collections.abc import Mapping
from threading import RLock

from flask import Flask, Blueprint, url_for
from werkzeug.urls import url_parse

from freezeyt import freeze


def unwrap_method(method):
    """Return the function object for the given method object."""
    try:
        return method.__func__
    except AttributeError:
        # Not a method.
        return method

class Freezer:
    """Replacement form Frozen-flask's Freezer"""
    def __init__(
        self,
        with_static_files=True,
        with_no_argument_rules=True,
    ):
        self.generators = []
        if with_static_files:
            self.register_generator(self.static_files_urls)
        if with_no_argument_rules:
            self.register_generator(self.no_argument_rules_urls)

    def register_generator(self, function):
        self.generators.append(function)

    def init_app(self, app):
        self.app = app
        if app:
            app.config.setdefault('FREEZER_STATIC_IGNORE', [])

    def freeze(self):
        freeze_info = None
        handling_url_for = False

        def start_hook(new_freeze_info):
            nonlocal freeze_info, handling_url_for
            freeze_info = new_freeze_info
            handling_url_for = True

        lock = RLock()
        def handle_url_for(endpoint, values):
            nonlocal handling_url_for
            with lock:
                if handling_url_for:
                    handling_url_for = False
                    values = {**values, '_external': True}
                    freeze_info.add_url(url_for(endpoint, **values))
                    handling_url_for = True

        # Do not use app.url_defaults() as we want to insert at the front
        # of the list to get unmodifies values.
        self.app.url_default_functions.setdefault(None, []).insert(0, handle_url_for)

        def generator(app):
            return self.all_urls()

        redirect_policy = self.app.config.get(
            'FREEZER_REDIRECT_POLICY', 'follow'
        )

        # Frozen-flask's freeze function returns a set of relative URLs
        # without query or fragment parts
        recorded_urls = set()
        def record_url(task_info):
            url = task_info.get_a_url()

            # make the URL relative
            assert url.startswith(prefix), (url, prefix)
            url = '/' + url[len(prefix):]

            # Remove query & fragment
            parsed = url_parse(url)
            parsed = parsed.replace(query='', fragment='')

            recorded_urls.add(parsed.to_url())

        prefix = 'http://example.com:8000/'
        config = {
            'prefix': prefix,
            'output': 'dict',
            'extra_pages': [generator],
            'redirect_policy': redirect_policy,
            'hooks': {
                'page_frozen': record_url,
                'start': start_hook,
            },
        }
        freeze(self.app, config)
        return recorded_urls

    def _static_rules_endpoints(self):
        """
        Yield the 'static' URL rules for the app and all blueprints.
        """
        send_static_file = Flask.send_static_file
        # Assumption about a Flask internal detail:
        # Flask and Blueprint inherit the same method.
        # This will break loudly if the assumption isn't valid anymore in
        # a future version of Flask
        assert Blueprint.send_static_file is send_static_file

        for rule in self.app.url_map.iter_rules():
            view = self.app.view_functions[rule.endpoint]
            if unwrap_method(view) is send_static_file:
                yield rule.endpoint

    def static_files_urls(self):
        """
        URL generator for static files for app and all registered blueprints.
        """
        for endpoint in self._static_rules_endpoints():
            # endpoint = 'static'
            view = self.app.view_functions[endpoint]
            app_or_blueprint = view.__self__
            root = app_or_blueprint.static_folder
            ignore = self.app.config['FREEZER_STATIC_IGNORE']
            if root is None or not Path(root).is_dir():
                # No 'static' directory for this app/blueprint.
                continue
            for filename in walk_directory(root, ignore=ignore):
                yield endpoint, {'filename': filename}

    def all_urls(self):
        with self.app.test_request_context():
            for generator in self.generators:
                for generated in generator():
                    if isinstance(generated, str):
                        yield generated
                        continue
                    elif isinstance(generated, Mapping):
                        endpoint = generator.__name__
                        values = generated
                    elif len(generated) == 2:
                        endpoint, values = generated
                    else:
                        endpoint, values, last_mod = generated
                    yield url_for(endpoint, **values)

    def no_argument_rules_urls(self):
        for rule in self.app.url_map.iter_rules():
            if not rule.arguments and 'GET' in rule.methods:
                yield rule.endpoint, {}

def walk_directory(root, ignore=None):
    for path in Path(root).glob('**/*'):
        if not path.is_dir():
            yield str(path.relative_to(root))

class FrozenFlaskWarning(Warning):
    pass

class MissingURLGeneratorWarning(Warning):
    pass

class MimetypeMismatchWarning(Warning):
    pass

class NotFoundWarning(Warning):
    pass

class RedirectWarning(Warning):
    pass
