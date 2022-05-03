import shutil

from . import compat
from .saver import Saver


class DirectoryExistsError(Exception):
    """Attempt to overwrite directory that doesn't contain freezeyt output"""


class FileSaver(Saver):
    """Outputs frozen pages as files on the filesystem.

    base - Filesystem base path (eg. /tmp/)
    prefix - Base URL to deploy web app in production
        (eg. url_parse('http://example.com:8000/foo/')
    """
    def __init__(self, base_path, prefix):
        self.base_path = base_path.resolve()
        self.prefix = prefix

    async def prepare(self):
        if self.base_path.exists():
            has_files = list(self.base_path.iterdir())
            has_index = self.base_path.joinpath('index.html').exists()
            if has_files and not has_index:
                raise DirectoryExistsError(
                    f'Will not overwrite directory {self.base_path}: it '
                    + 'contains files that do not look like a frozen website. '
                    + 'If you are sure, remove the directory before running '
                    + 'freezeyt.'
                )
            shutil.rmtree(self.base_path)

    async def save_to_filename(self, filename, content_iterable):
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        loop = compat.get_running_loop()

        absolute_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(absolute_filename, "wb") as f:
            for item in content_iterable:
                await loop.run_in_executor(None, f.write, item)

    async def open_filename(self, filename):
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        return open(absolute_filename, 'rb')

    async def finish(self, success: bool, cleanup: bool):
        """Delete incomplete directory after a failed freeze.
        """
        if not success and cleanup and self.base_path.exists():
            shutil.rmtree(self.base_path)
