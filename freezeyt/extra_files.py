import base64
from pathlib import Path
import collections.abc
from typing import Mapping, Iterator, Tuple, Union
import sys

from freezeyt.util import get_url_part


if sys.version_info > (3, 8):
    from typing import Literal
    literal_content = Literal["content"]
    literal_path = Literal["path"]
else:
    literal_content = str
    literal_path = str


def get_extra_files(
    config: Mapping
) -> Iterator[Union[
    Tuple[str, literal_content, bytes],
    Tuple[str, literal_path, Path],
]]:
    """Extracts the extra_files from Freezeyt configuration.

    Returns an iterator with two kinds of items:
    - (url_path, "content", bytes): the page at `url_path` should have the
      contents given in `bytes`.
    - (url_path, "path", path): the contents of the page at `url_path`
      should be read from `path` on disk, if it's a file.
      If it's a directory, the entire directory should be frozen at the
      `url_path` prefix.
    """
    extra_files_config = config.get('extra_files')
    if extra_files_config is not None:
        for text, content in extra_files_config.items():
            url_part = get_url_part(text)
            if isinstance(content, str):
                yield url_part, "content", content.encode()
            elif isinstance(content, bytes):
                yield url_part, "content", content
            elif isinstance(content, collections.abc.Mapping):
                if 'base64' in content:
                    content = base64.b64decode(content['base64'])
                    yield url_part, "content", content
                elif 'copy_from' in content:
                    path = Path(content['copy_from']).resolve()
                    yield url_part, "path", path
                else:
                    raise ValueError(
                        'a mapping in extra_files must contain '
                        + '"base64" or "copy_from"'
                    )
            else:
                raise TypeError(
                    'extra_files values must be bytes, str or mappings;'
                    + f' got a {type(content).__name__}'
                )

def get_url_parts_from_directory(url_part: str, path: Path) -> Iterator[str]:
    """Yield the names of all files in `path`, prefixed by `url_part`.

    If `path` is a directory, yield all of its contents recursively.
    """
    if path.is_dir():
        for subpath in path.iterdir():
            yield from get_url_parts_from_directory(
                url_part=url_part.rstrip('/') + '/' + subpath.name,
                path=subpath,
            )
    else:
        yield url_part
