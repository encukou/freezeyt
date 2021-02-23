from pathlib import Path

class Freezer:
    def register_generator(self, function):
        pass

    def init_app(self, app):
        pass

    def freeze(self):
        pass

    def all_urls(self):
        return []

def walk_directory(root):
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
