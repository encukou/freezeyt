from io import BytesIO
from pathlib import Path


class DictSaver:
    """Outputs frozen pages into a dict.

    prefix - Base URL to deploy web app in production
        (eg. url_parse('http://example.com:8000/foo/')
    """
    def __init__(self, prefix):
        self.prefix = prefix
        self.contents = {}

    def prepare(self):
        """DictSaver doesn't need any preparation"""

    def save_to_filename(self, filename, content_iterable):
        parts = Path(filename).parts

        target = self.contents
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = b''.join(content_iterable)

    def open_filename(self, filename):
        parts = Path(filename).parts
        target = self.contents
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        return BytesIO(target[parts[-1]])

    def get_result(self):
        return self.contents
