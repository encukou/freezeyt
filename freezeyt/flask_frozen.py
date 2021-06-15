from pathlib import Path
from collections.abc import Mapping
from threading import RLock
from urllib.parse import unquote
import shutil
import tempfile
from fnmatch import fnmatch
import mimetypes
import warnings

from flask import Flask, Blueprint, url_for, request, send_from_directory
from werkzeug.urls import url_parse

from freezeyt import freeze, url_to_path
from freezeyt import ExternalURLError, RelativeURLError, UnexpectedStatus

PREFIX = 'http://localhost:80/'

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
        app=None,
        with_static_files=True,
        with_no_argument_rules=True,
        log_url_for=True,
    ):
        self.generators = []
        if with_static_files:
            self.register_generator(self.static_files_urls)
        if with_no_argument_rules:
            self.register_generator(self.no_argument_rules_urls)
        self.log_url_for = log_url_for
        if app:
            self.init_app(app)

    def register_generator(self, function):
        self.generators.append(function)

    def init_app(self, app):
        self.app = app
        if app:
            app.config.setdefault('FREEZER_STATIC_IGNORE', [])

    @property
    def root(self):
        root = self.app.config.get('FREEZER_DESTINATION', 'build')
        return str(Path(self.app.root_path).resolve() / root)

    def freeze(self):
        freeze_info = None
        handling_url_for = False

        def start_hook(new_freeze_info):
            nonlocal freeze_info, handling_url_for
            freeze_info = new_freeze_info
            handling_url_for = True

        if self.log_url_for:
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
            default_funcs = self.app.url_default_functions
            default_funcs.setdefault(None, []).insert(0, handle_url_for)

        def generator(app):
            return self.all_urls()

        redirect_policy = self.app.config.get(
            'FREEZER_REDIRECT_POLICY', 'follow'
        )

        if not self.app.config.get('FREEZER_REMOVE_EXTRA_FILES', True):
            kept_file_patterns = ['*']
        else:
            kept_file_patterns = self.app.config.get('FREEZER_DESTINATION_IGNORE', [])

        if self.app.config.get('FREEZER_SKIP_EXISTING', False):
            kept_file_patterns = ['*']

        if kept_file_patterns:
            kept_file_dir = save_kept_files(self.root, kept_file_patterns)
        else:
            kept_file_dir = None

        # Frozen-flask's freeze function returns a set of relative URLs
        # without query or fragment parts
        recorded_urls = set()
        def record_url(task_info):
            url = make_relative_url(PREFIX, task_info.get_a_url())
            recorded_urls.add(url)

        config = {
            'prefix': PREFIX,
            'output': self.root,
            'extra_pages': [generator],
            'redirect_policy': redirect_policy,
            'hooks': {
                'page_frozen': record_url,
                'start': start_hook,
            },
        }
        default_mimetype = self.app.config.get('FREEZER_DEFAULT_MIMETYPE')
        if default_mimetype:
            config['default_mimetype'] = default_mimetype
        if self.app.config.get('FREEZER_IGNORE_404_NOT_FOUND', False):
            config['404_handler'] = self.ignore_404
        try:
            if Path(self.root).exists():
                shutil.rmtree(self.root)
            freeze(self.app, config)
        except (ExternalURLError, RelativeURLError):
            raise ValueError('External URLs not supported')
        except UnexpectedStatus as e:
            relative_url = make_relative_url(PREFIX, e.url.to_url())
            raise ValueError(f"Unexpected status '{e.status}' on URL {relative_url}")
        finally:
            # Frozen-Flask always creates the output directory;
            # Freezeyt may remove it on errors.
            Path(self.root).mkdir(exist_ok=True)
            if kept_file_dir:
                restore_kept_files(
                    kept_file_dir, self.root,
                    restore_all=self.app.config.get('FREEZER_SKIP_EXISTING', False),
                )

        return recorded_urls

    def ignore_404(self, task, status, headers):
        warnings.warn(f'Page not found: {task.get_a_url()}!', NotFoundWarning)
        return True

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
            elif rule.endpoint == 'static':
                yield rule.endpoint

    def static_files_urls(self):
        """
        URL generator for static files for app and all registered blueprints.
        """
        for endpoint in self._static_rules_endpoints():
            # endpoint = 'static'
            view = self.app.view_functions[endpoint]
            app_or_blueprint = getattr(view, '__self__', self.app)
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

    def make_static_app(self):
        """Return a Flask application serving the build destination."""
        root = self.root

        def dispatch_request():
            print(request)
            filename = url_to_path(PREFIX, request.url)

            # Override the default mimeype from settings
            guessed_type, guessed_encoding = mimetypes.guess_type(filename)
            if not guessed_type:
                guessed_type = self.app.config['FREEZER_DEFAULT_MIMETYPE']

            return send_from_directory(root, filename, mimetype=guessed_type)

        app = Flask(__name__)
        # Do not use the URL map
        app.dispatch_request = dispatch_request
        return app

def make_relative_url(prefix: str, url: str):
    # make the URL relative
    assert url.startswith(prefix), (url, prefix)
    url = '/' + url[len(prefix):]

    # Remove query & fragment
    parsed = url_parse(url)
    parsed = parsed.replace(query='', fragment='')

    url = unquote(parsed.to_url())
    return url


def save_kept_files(root, kept_file_patterns):
    """Copy all files named by "kept_file_patterns" to a temporary directory"""

    root_path = Path(root)
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)

    def keep(filename):
        src = root_path / filename
        dest = temp_path / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    basename_kept = [n for n in kept_file_patterns if '/' not in n]
    path_kept = [n.strip('/') for n in kept_file_patterns if '/' in n]
    for filename in walk_directory(root):
        name = Path(filename).name
        if any(fnmatch(name, pattern) for pattern in basename_kept):
            keep(filename)
        elif any(fnmatch(filename, pattern) for pattern in path_kept):
            keep(filename)

    return temp_dir

def restore_kept_files(kept_file_dir, root, restore_all=False):
    """Restore files saved by save_kept_files."""
    root_path = Path(root)
    temp_path = Path(kept_file_dir.name)
    for filename in walk_directory(kept_file_dir.name):
        src = temp_path / filename
        dest = root_path / filename
        if restore_all or not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
    kept_file_dir.cleanup()

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
