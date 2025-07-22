import os
import stat
import asyncio
from pathlib import Path, PurePosixPath

from . import compat
from .saver import Saver
from .urls import PrefixURL

from typing import Callable, Iterable, BinaryIO


class DirectoryExistsError(Exception):
    """Attempt to overwrite directory that doesn't contain freezeyt output"""


class FileSaver(Saver):
    """Outputs frozen pages as files on the filesystem.

    base - Filesystem base path (eg. /tmp/)
    prefix - Base URL to deploy web app in production
        (eg. url_parse('http://example.com:8000/foo/')
    """
    @staticmethod
    def add_write_flag(
        function: Callable[[str], None],
        path: str,
        exception: BaseException,
    ) -> None:
        """A function that adds a write attribute/flag for a path where such an attribute is missing. This function is not necessary on Linux, but on Windows, attempting to delete a file where such an attribute is missing will raise an exception.

        Function parameters are:
        function: function which raised the exception,
        path: path name passed to function,
        excinfo: exception information returned by sys.exc_info()
        """
        if not os.access(path, os.W_OK):
            os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
            return function(path)
        else:
            raise exception

    def __init__(self, base_path: Path, prefix: PrefixURL):
        self.base_path = base_path.resolve()
        self.prefix = prefix

    async def prepare(self) -> None:
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

            compat.rmtree(self.base_path, onexc=self.add_write_flag)

    async def save_to_filename(
        self,
        filename: PurePosixPath,
        content_iterable: Iterable[bytes],
    ) -> None:
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        loop = asyncio.get_running_loop()

        absolute_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(absolute_filename, "wb") as f:
            for item in content_iterable:
                await loop.run_in_executor(None, f.write, item)

    async def open_filename(self, filename: PurePosixPath) -> BinaryIO:
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        return open(absolute_filename, 'rb')

    async def finish(self, success: bool, cleanup: bool) -> None:
        """Delete incomplete directory after a failed freeze."""
        if not success and cleanup and self.base_path.exists():
            compat.rmtree(self.base_path)
