import io
import json
import pytest

from freezeyt.util import parse_mimetype_db

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
        {"image/jpeg": ["jpeg","jpg","jpe"]}
    ),
    "no_catch": (
        {
            "audio/melp600": {"source": "iana"},
            "audio/mhas": {"source": "iana"}
        },
        {}
    ),
    "many_catch": (
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
        },
        {
            "audio/wav": ["wav"],
            "audio/wave": ["wav"],
            "audio/webm": ["weba"]
        }
    )
}

@pytest.mark.parametrize('testcase', TESTCASES)
def test_parse_mimetype_db(monkeypatch, testcase):
    db_content, expected = TESTCASES[testcase]
    def mocked_open(file):
        content = json.dumps(db_content)
        return io.StringIO(content)

    monkeypatch.setattr('builtins.open', mocked_open)

    result = parse_mimetype_db('path/to/file')
    assert result == expected
