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
        {
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "jpe": "image/jpeg",
        }
    ),
    "catch_conflict_mimetypes": (
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
            "wav": "audio/wav",
            "weba": "audio/webm",
        }
    ),
    "basic": (
        {
            "application/onenote": {
                "source": "apache",
                "extensions": ["onetoc","onetoc2","onetmp","onepkg"]
            },
            "application/vnd.cups-ppd": {
                "source": "iana",
                "extensions": ["ppd"]
            },
            "application/vnd.curl.car": {
                "source": "apache",
                "extensions": ["car"]
        },
        },
        {
            "onetoc": "application/onenote",
            "onetoc2": "application/onenote",
            "onetmp": "application/onenote",
            "onepkg": "application/onenote",
            "ppd": "application/vnd.cups-ppd",
            "car": "application/vnd.curl.car",
            # default suffix
            "3gpp": "audio/3gpp",
            "sub": "image/vnd.dvb.subtitle",
            "exe": "application/octet-stream",
            "dmg": "application/octet-stream",

        }
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


def test_parse_mimetype_db_no_catch(monkeypatch):
    default_db = {
        "rtf": "application/rtf",
        "m4a": "audio/mp4",
        "msi": "application/octet-stream",
        "mpp": "application/vnd.ms-project",
        "ra": "audio/x-pn-realaudio",
        "prc": "application/x-mobipocket-ebook",
        "xlf": "application/x-xliff+xml",
        "ac": "application/pkix-attr-cert",
        "pcx": "image/vnd.zbrush.pcx",
        "rar": "application/vnd.rar",
        "xml": "application/xml",
        "obj": "application/x-tgif",
        "wmf": "application/x-msmetafile",
        "3gpp": "audio/3gpp",
        "sub": "image/vnd.dvb.subtitle",
        "exe": "application/octet-stream",
        "dmg": "application/octet-stream",
        "pages": "application/vnd.apple.pages",
        "x3db": "model/x3d+binary",
        "mp3": "audio/mp3",
        "key": "application/vnd.apple.keynote",
        "jpm": "image/jpm",
        "numbers": "application/vnd.apple.numbers",
        "pdb": "application/vnd.palm",
        "dll": "application/octet-stream",
        "asc": "application/pgp-signature",
        "org": "application/vnd.lotus-organizer",
        "ico": "image/vnd.microsoft.icon",
        "deb": "application/octet-stream",
        "x3dv": "model/x3d+vrml",
        "bmp": "image/bmp",
        "wav": "audio/wav",
        "emf": "application/x-msmetafile",
        "bdoc": "application/bdoc",
        "iso": "application/octet-stream",
        "wmz": "application/x-ms-wmz",
        "stl": "application/vnd.ms-pki.stl",
        "xsl": "application/xml",
    }
    mocked_func = mock_wrapper(
        {
            "application/mathml-presentation+xml": {
                "source": "iana",
                "compressible": True
            },
            "application/mathml-content+xml": {
                "source": "iana",
                "compressible": True
            }
        }
    )
    monkeypatch.setattr('builtins.open', mocked_func)
    result = parse_mimetype_db('some/path')

    assert result == default_db
