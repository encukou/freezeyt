import io
import json
import pytest

from freezeyt.freezer import parse_mimetype_db


TESTCASES = {
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

def mock_wrapper(db_content):

    def mocked_open(file):
        content = json.dumps(db_content)
        return io.StringIO(content)

    return mocked_open

@pytest.mark.parametrize('testcase', TESTCASES)
def test_parse_mimetype_db(monkeypatch, testcase):
    db_content, expected = TESTCASES[testcase]
    mocked_func = mock_wrapper(db_content)
    monkeypatch.setattr('builtins.open', mocked_func)

    result = parse_mimetype_db('path/to/file')
    for suffix in expected:
        assert result.get(suffix) == expected.get(suffix)

