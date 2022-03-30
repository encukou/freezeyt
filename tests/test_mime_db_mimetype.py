import pytest
import json

from testutil import context_for_test
from freezeyt import freeze
from freezeyt.freezer import parse_mime_db, mime_db_mimetype


PARSER_TEST_DATA = {
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
            "jpeg": {"image/jpeg"},
            "jpg": {"image/jpeg"},
            "jpe": {"image/jpeg"},
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
            "wav": {"audio/wav", "audio/wave"},
            "weba": {"audio/webm"},
            "exe": {
                "application/octet-stream",
                "application/x-msdownload",
                "application/x-msdos-program"
            },
            "dll": {"application/octet-stream", "application/x-msdownload"},
            "com": {"application/x-msdownload"},
            "bat": {"application/x-msdownload"},
            "msi": {"application/x-msdownload", "application/octet-stream"},
            "bin": {"application/octet-stream"}
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
    "low_up_mix": (
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
        {"wav": {"audio/wav", "audio/wave"}},
    )
}

@pytest.mark.parametrize('testname', PARSER_TEST_DATA)
def test_parse_mime_db(monkeypatch, testname):
    """Test func parse_mime_db that correct structure is parsed
    """
    mime_db, expected = PARSER_TEST_DATA[testname]
    result = parse_mime_db(mime_db)
    assert result == expected


def test_freeze_app_mock_mime_db(tmp_path):
    """Integration test with custom database, where is purposely
    set wrong mimetype for jpg format to be sure that custom db was really used.
    """
    MIMETYPE_DB = {
        "image/png": {
            "source": "iana",
            "compressible": False,
            "extensions": ["jpeg","jpg"]
        },
        'text/html': {
            "extensions": ["html"]
        }
    }
    builddir = tmp_path / 'build'
    db_path = tmp_path / "mime_db.json"

    with open(db_path, mode="w") as mime_db:
        json.dump(MIMETYPE_DB, mime_db)

    with context_for_test('app_wrong_mimetype') as module:
        freeze_config = {
            'output': str(builddir),
            'mime_db_file': str(db_path)
        }

        freeze(module.app, freeze_config)

    assert (builddir / 'index.html').exists()
    assert (builddir / 'image.jpg').exists()


MIME_DB_TEST_DATA = {
    "simple": (
        {"wav": {"audio/wav", "audio/wave"}},
        "https://example.test/hello.wav",
        {"audio/wav", "audio/wave"}
    ),
    "without_suffix": (
        {"wav": {"audio/wav", "audio/wave"}},
        "https://example.test/hello",
        None
    )
}
@pytest.mark.parametrize('testname', MIME_DB_TEST_DATA)
def test_get_filetype_from_suffix(testname):
    """Test the guessing filetype by mime-db mimetype from file suffix.
    """
    suffixes_db, url, expected = MIME_DB_TEST_DATA[testname]
    result = mime_db_mimetype(suffixes_db, url)
    assert result == expected
