from typing import Optional, List, Mapping, Dict
from mimetypes import guess_type
from pathlib import PurePosixPath
import functools
import json

from werkzeug.datastructures import Headers
from werkzeug.http import parse_options_header

from freezeyt.util import WrongMimetypeError
from freezeyt.util import import_variable_from_module

def convert_mime_db(mime_db: Mapping) -> Dict[str, List[str]]:
    """Convert mime-db value 'extensions' to become a key
    and origin mimetype key to dict value as item of list.
    """
    converted_db: Dict[str, List[str]] = {}
    for mimetype, opts in mime_db.items():
        extensions = opts.get('extensions')
        if extensions is not None:
            for extension in extensions:
                mimetypes = converted_db.setdefault(extension.lower(), [])
                mimetypes.append(mimetype.lower())

    return converted_db


def mime_db_mimetype(mime_db: dict, url: str) -> Optional[List[str]]:
    """Determines file MIME type from file suffix. Decisions are made
    by mime-db rules.
    """
    suffix = PurePosixPath(url).suffix[1:].lower()

    return mime_db.get(suffix)


def default_mimetype(url: str) -> Optional[List[str]]:
    """Returns file mimetype as a string from mimetype.guess_type.
    file mimetypes are guessed from file suffix.
    """
    file_mimetype, encoding = guess_type(url)
    if file_mimetype is None:
        return None
    else:
        return [file_mimetype]


def check_mimetype(
    url_path, headers,
    default='application/octet-stream', *, get_mimetype=default_mimetype,
):
    """Ensure mimetype sent from headers with file mimetype guessed
    from its suffix.
    Raise WrongMimetypeError if they don't match.
    """
    if url_path.endswith('/'):
        # Directories get saved as index.html
        url_path = 'index.html'
    file_mimetypes = get_mimetype(url_path)
    if file_mimetypes is None:
        file_mimetypes = [default]

    headers = Headers(headers)
    headers_mimetype, encoding = parse_options_header(
        headers.get('Content-Type')
    )

    if isinstance(file_mimetypes, str):
        raise TypeError("get_mimetype result must not be a string")

    if headers_mimetype.lower() not in (m.lower() for m in file_mimetypes):
        raise WrongMimetypeError(file_mimetypes, headers_mimetype, url_path)


def get_mimetype_checker(config):
    get_mimetype = config.get('get_mimetype', default_mimetype)
    mime_db_file = config.get('mime_db_file', None)

    if mime_db_file:
        with open(mime_db_file) as file:
            mime_db = json.load(file)

        mime_db = convert_mime_db(mime_db)
        get_mimetype = functools.partial(mime_db_mimetype, mime_db)

    if isinstance(get_mimetype, str):
        get_mimetype = import_variable_from_module(get_mimetype)

    return functools.partial(
        check_mimetype,
        default=config.get('default_mimetype', 'application/octet-stream'),
        get_mimetype=get_mimetype
    )
