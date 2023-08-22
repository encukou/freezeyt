import json
from typing import Dict, Tuple

import pytest

from testutil import context_for_test
from freezeyt import freeze
from freezeyt.mimetype_check import convert_mime_db, mime_db_mimetype


CONVERSION_TESTCASES: Dict[str, Tuple[Dict, Dict]] = {
    "catch_jpeg": (
        {
            "application/3gpdash-qoe-report+xml": {
                "source": "iana",
                "charset": "UTF-8",
                "compressible": True
            },
            "image/jpeg": {
                "source": "iana",
                "compressible": False,
                "extensions": ["jpeg","jpg","jpe"]
            }
        },
        {
            "jpeg": ["image/jpeg"],
            "jpg": ["image/jpeg"],
            "jpe": ["image/jpeg"],
        }
    ),
    "catch_many_mimetypes": (
        {
            "audio/wav": {
                "compressible": False,
                "extensions": ["wav"]
            },
            "audio/wave": {
                "compressible": False,
                "extensions": ["wav"]
            },
            "audio/webm": {
                "source": "apache",
                "compressible": False,
                "extensions": ["weba"]
            },
            "application/x-msdos-program": {
                "extensions": ["exe"]
            },
            "application/x-msdownload": {
                "source": "apache",
                "extensions": ["exe","dll","com","bat","msi"]
            },
            "application/octet-stream": {
                "source": "iana",
                "compressible": False,
                "extensions": ["bin","exe","dll","msi"]
            },
        },
        {
            "wav": ["audio/wav", "audio/wave"],
            "weba": ["audio/webm"],
            "exe": [
                "application/x-msdos-program",
                "application/x-msdownload",
                "application/octet-stream"
            ],
            "dll": ["application/x-msdownload", "application/octet-stream"],
            "com": ["application/x-msdownload"],
            "bat": ["application/x-msdownload"],
            "msi": ["application/x-msdownload", "application/octet-stream"],
            "bin": ["application/octet-stream"]
        }
    ),
    "no_catch": (
        {
            "application/vnd.cybank": {
                "source": "iana"
            },
            "application/vnd.cyclonedx+json": {
                "source": "iana",
                "compressible": True
            },
        },
        {}
    ),
    "capitals_used": (
        {
            "auDio/Wav": {
                "compressible": False,
                "extensions": ["wAv"]
            },
            "aUdio/waVe": {
                "compressible": False,
                "extensions": ["waV"]
            },
        },
        {
            "wav": ["audio/wav", "audio/wave"]
        },
    )
}

@pytest.mark.parametrize('testname', CONVERSION_TESTCASES)
def test_mime_db_conversion(testname):
    """Test if the convert process of mime-db structure
    to new one is performed correctly.
    """
    mime_db, expected = CONVERSION_TESTCASES[testname]
    result = convert_mime_db(mime_db)
    assert result == expected


def test_modified_mime_db_file(tmp_path):
    """Integration test with modified mime-db, where is purposely
    set wrong extensions for MIME image/png to check if our db was used.

    """
    MIME_DB_TO_JSON = {
        "image/png": {
            "source": "iana",
            "compressible": False,
            "extensions": ["Jpeg","jPg"]
        },
        'text/html': {
            "extensions": ["htmL"]
        }
    }
    builddir = tmp_path / 'build'
    db_path = tmp_path / "mime_db.json"

    with open(db_path, mode="w") as mime_db:
        json.dump(MIME_DB_TO_JSON, mime_db)

    with context_for_test('app_wrong_mimetype') as module:
        freeze_config = {
            'output': str(builddir),
            'mime_db_file': str(db_path)
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    # 'image.jpg' exists because we linked jpg extension with MIME 'image/png'
    assert (builddir / 'image.jpg').exists()


GET_MIME_TYPE_TESTCASES = {
    "simple": (
        {"wav": ["audio/wav", "audio/wave"]},
        "https://example.test/hello.wav",
        ["audio/wav", "audio/wave"]
    ),
    "capital_file_suffix": (
        {"wav": ["audio/wav", "audio/wave"]},
        "https://example.test/hello.WAV",
        ["audio/wav", "audio/wave"]
    ),
    "without_suffix": (
        {"wav": ["audio/wav", "audio/wave"]},
        "https://example.test/hello",
        None
    )
}
@pytest.mark.parametrize('testname', GET_MIME_TYPE_TESTCASES)
def test_get_MIME_type_from_suffix(testname):
    """Test the return values of mime_db_mimetype
    """
    converted_mime_db, url, expected = GET_MIME_TYPE_TESTCASES[testname]
    result = mime_db_mimetype(converted_mime_db, url)
    assert result == expected
