from io import BytesIO
from pathlib import PurePosixPath
from typing import Dict, Union, Iterable

from .saver import Saver


# Type for holding simulated directory contents.
DictSaverContents = Dict[
    str,  # filename; maps to either:
    Union[
        bytes,  # file contents, or
        'DictSaverContents',  # a subdirectory.
    ]
]

class DictSaver(Saver):
    """Outputs frozen pages into a dict.
    """
    def __init__(self):
        self.contents: DictSaverContents = {}

    async def save_to_filename(
        self,
        filename: PurePosixPath,
        content_iterable: Iterable[bytes],
    ) -> None:
        path = PurePosixPath(filename)
        if path.is_absolute():
            raise ValueError('filename must be relative')
        parts = path.parts
        if not parts:
            raise IsADirectoryError('.')

        target: DictSaverContents = self.contents
        for part in parts[:-1]:
            new_target = target.setdefault(part, {})
            if not isinstance(new_target, dict):
                raise NotADirectoryError(PurePosixPath(*parts[:-1]))
            target = new_target
        if isinstance(target.get(parts[-1]), dict):
            raise IsADirectoryError(filename)
        target[parts[-1]] = b''.join(content_iterable)

    async def open_filename(self, filename: PurePosixPath) -> BytesIO:
        path = PurePosixPath(filename)
        if path.is_absolute():
            raise ValueError('filename must be relative')
        parts = path.parts
        if not parts:
            raise IsADirectoryError('.')

        target: DictSaverContents = self.contents
        for part in parts[:-1]:
            new_target = target.setdefault(part, {})
            if not isinstance(new_target, dict):
                raise NotADirectoryError(PurePosixPath(*parts[:-1]))
            target = new_target
        try:
            contents = target[parts[-1]]
        except KeyError:
            raise FileNotFoundError(filename)
        if isinstance(contents, dict):
            raise IsADirectoryError(filename)
        return BytesIO(contents)

    async def finish(self, success: bool, cleanup: bool) -> DictSaverContents:
        return self.contents
