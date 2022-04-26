from io import BytesIO
from pathlib import PurePosixPath

from .saver import Saver


class DictSaver(Saver):
    """Outputs frozen pages into a dict.

    prefix - Base URL to deploy web app in production
        (eg. url_parse('http://example.com:8000/foo/')
    """
    def __init__(self, prefix):
        self.prefix = prefix
        self.contents = {}

    async def save_to_filename(self, filename, content_iterable):
        parts = PurePosixPath(filename).parts

        target = self.contents
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = b''.join(content_iterable)

    async def open_filename(self, filename):
        parts = PurePosixPath(filename).parts
        target = self.contents
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        return BytesIO(target[parts[-1]])

    async def finish(self, success, cleanup):
        return self.contents
