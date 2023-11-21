from io import BytesIO
from pathlib import PurePosixPath
from typing import Dict, Union, Iterable, Tuple

from .saver import Saver


# Type for holding simulated directory contents.
DictSaverContents = Dict[
    str,  # filename; maps to either:
    Union[
        bytes,  # file content, or
        'DictSaverContents',  # a subdirectory.
    ]
]

class DictSaver(Saver):
    """Outputs frozen pages into a dict.
    """
    def __init__(self):
        self.root_dir: DictSaverContents = {}

    async def save_to_filename(
        self,
        filepath: PurePosixPath,
        content_iterable: Iterable[bytes],
    ) -> None:
        parent_dir, name = get_parent_and_name(self.root_dir, filepath)

        if isinstance(parent_dir.get(name), dict):
            raise IsADirectoryError(filepath)
        parent_dir[name] = b''.join(content_iterable)

    async def open_filename(self, filepath: PurePosixPath) -> BytesIO:
        parent_dir, name = get_parent_and_name(self.root_dir, filepath)

        try:
            file_content = parent_dir[name]
        except KeyError:
            raise FileNotFoundError(filepath)
        if isinstance(file_content, dict):
            raise IsADirectoryError(filepath)
        return BytesIO(file_content)

    async def finish(self, success: bool, cleanup: bool) -> DictSaverContents:
        return self.root_dir

def get_parent_and_name(
    root_dir: DictSaverContents,
    filepath: PurePosixPath,
) -> Tuple[DictSaverContents, str]:
    """Return a dict representing the parent directory of the given file, and
    the name of the file.

    root_dir: a dict representing the root directory (DictSaver.root_dir)
    filepath: relative path to the file
    """
    path = PurePosixPath(filepath)
    if path.is_absolute():
        raise ValueError('filepath must be relative')
    parts = path.parts
    if not parts:
        raise IsADirectoryError('.')

    current_directory: DictSaverContents = root_dir
    for part in parts[:-1]:
        new_curdir = current_directory.setdefault(part, {})
        if not isinstance(new_curdir, dict):
            raise NotADirectoryError(PurePosixPath(*parts[:-1]))
        current_directory = new_curdir

    return current_directory, parts[-1]
