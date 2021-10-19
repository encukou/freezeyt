import shutil
import os
import sys
from freezeyt.util import FileWrapper
from typing import Optional, Callable

from . import compat

try:
    # sendfile is not available on all platforms.
    # If it is available, we can use it to speed up saving "static" files
    sendfile: Optional[Callable] = os.sendfile
except AttributeError:
    sendfile = None


class DirectoryExistsError(Exception):
    """Attempt to overwrite directory that doesn't contain freezeyt output"""


class FileSaver:
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
        global sendfile
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        loop = compat.get_running_loop()

        absolute_filename.parent.mkdir(parents=True, exist_ok=True)

        with open(absolute_filename, "wb") as f:
            if sendfile and isinstance(content_iterable, FileWrapper):
                # Optimization for systems that support os.sendfile
                try:
                    fileno_method = content_iterable.file.fileno
                except AttributeError:
                    pass
                else:
                    if sys.platform == 'linux':
                        offset = None
                    else:
                        offset = content_iterable.file.tell()
                    fileno = fileno_method()
                    try:
                        await loop.run_in_executor(
                            None, sendfile,
                            f.fileno(), fileno, offset, sys.maxsize,
                        )
                    except OSError:
                        # This system probably doesn't support copying
                        # regular files with os.sendfile.
                        # Don't try it in the future.
                        sendfile = None
                    else:
                        # Done!
                        return

            for item in content_iterable:
                await loop.run_in_executor(None, f.write, item)

    async def open_filename(self, filename):
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        return open(absolute_filename, 'rb')
