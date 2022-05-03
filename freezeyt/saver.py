import abc
from pathlib import PurePosixPath
from typing import BinaryIO, Any, Iterable

class Saver(abc.ABC):
    async def prepare(self):
        """Initialize the saver."""

    @abc.abstractmethod
    async def save_to_filename(
        self,
        filename: PurePosixPath,
        content_iterable: "Iterable[bytes]",
    ) -> None:
        """Save the given bytes to the given path"""

    @abc.abstractmethod
    async def open_filename(
        self,
        filename: PurePosixPath,
    ) -> BinaryIO:
        """Open the given path for reading bytes"""

    async def finish(self, success: bool, cleanup: bool) -> Any:
        """Clean up after a freeze and return the result, if any.

        success: true if the freeze was successful
        cleanup: If true, clean up after failed freezes
        """
        return None
