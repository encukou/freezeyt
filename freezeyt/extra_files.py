import base64
from pathlib import Path
import collections.abc
from typing import Mapping, Iterator, Tuple, Literal, Union

def get_extra_files(
    config: Mapping
) -> Iterator[Union[
    Tuple[str, Literal["content"], bytes],
    Tuple[str, Literal["path"], Path],
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
        for url_part, content in extra_files_config.items():
            if isinstance(content, str):
                yield url_part, "content", content.encode()
            elif isinstance(content, bytes):
                yield url_part, "content", content
            elif isinstance(content, collections.abc.Mapping):
                if 'base64' in content:
                    content = base64.b64decode(content['base64'])
                    yield url_part, "content", content
                elif 'copy_from' in content:
                    yield url_part, "path", Path(content['copy_from'])
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
