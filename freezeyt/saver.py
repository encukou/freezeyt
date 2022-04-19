
from pathlib import PurePosixPath
from typing import BinaryIO, Any
from collections.abc import Iterable

class Saver:
    async def prepare(self):
        """Initialize the saver."""

    async def save_to_filename(
        self,
        filename: PurePosixPath,
        content_iterable: Iterable[bytes],
    ) -> None:
        raise NotImplementedError('{type(self)} needs to implement save_to_filename')

    async def open_filename(
        self,
        filename: PurePosixPath,
    ) -> BinaryIO:
        raise NotImplementedError('{type(self)} needs to implement save_to_filename')

    async def finish(self, success: bool, cleanup: bool) -> Any:
        """Clean up after a freeze and return the result, if any.

        success: true if the freeze was successful
        cleanup: If true, clean up after failed freezes
        """
        return None
