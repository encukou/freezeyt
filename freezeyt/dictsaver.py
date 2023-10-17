from io import BytesIO
from pathlib import PurePosixPath
from typing import Iterable, Union

from .saver import Saver
from .types import AbsoluteURL


Contents_T = dict[str, Union[bytes, 'Contents_T']]

class DictSaver(Saver):
    """Outputs frozen pages into a dict.

    prefix - Base URL to deploy web app in production
        (eg. url_parse('http://example.com:8000/foo/')
    """
    def __init__(self, prefix: AbsoluteURL):
        self.prefix = prefix
        self.contents: Contents_T = {}

    async def save_to_filename(
        self,
        filename: PurePosixPath,
        content_iterable: Iterable[bytes],
    ) -> None:
        parts = filename.parts
        target = find_directory(self.contents, parts[:-1])
        target[parts[-1]] = b''.join(content_iterable)

    async def open_filename(self, filename: PurePosixPath) -> BytesIO:
        parts = filename.parts
        target = find_directory(self.contents, parts[:-1])
        file_content = target[parts[-1]]
        if isinstance(file_content, dict):
            raise IsADirectoryError(filename)
        return BytesIO(file_content)

    async def finish(self, success: bool, cleanup: bool) -> Contents_T:
        return self.contents

def find_directory(
    root_contents: Contents_T,
    dir_names: Iterable[str],
) -> Contents_T:
    current_contents = root_contents
    for dir_name in dir_names:
        new_contents = current_contents.setdefault(dir_name, {})
        if not isinstance(new_contents, dict):
            raise NotADirectoryError('/'.join(dir_names))
        current_contents = new_contents
    return current_contents
