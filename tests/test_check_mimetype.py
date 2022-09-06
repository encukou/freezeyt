import pytest

from freezeyt.mimetype_check import check_mimetype


TEST_DATA = {
    'normal_html': (
        'http://localhost:8000/index.html',
        [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', '164'),
        ],
    ),

    'jpg_X_png_fail': (
        'http://localhost:8000/index.jpg',
        [
            ('Content-Type', 'image/png'),
            ('Content-Length', '654'),
        ],
    ),

    'missing_content_type_fail': (
        'http://localhost:8000/index.html', [('Content-Length', '164')]
    ),

    'case_insensitive_content_type': (
        'http://localhost:8000/index.html',
        [
            ('Content-Type', 'TEXT/HTML; charset=utf-8'),
            ('Content-Length', '164'),
        ],
    ),

    'case_insensitive_file': (
        'http://localhost:8000/index.HTML',
        [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', '164'),
        ],
    ),

    'case_insensitive_headers_fail': (
        'http://localhost:8000/index.jpg',
        [
            ('CONTENT-TYPE', 'IMAGE/PNG'),
            ('Content-Length', '654'),
        ],
    ),

    'case_insensitive_headers': (
        'http://localhost:8000/index.jpg',
        [
            ('coNtENT-TypE', 'IMAgE/JpEG'),
            ('Content-Length', '654'),
        ],
    ),

    # The content-type for JPEG images is standardized: `image/jpeg` (case insensitive).
    # The file extension is not standardized; the default recognizer guesses that
    # both `.jpg` or `.jpeg` mean JPEG images.
    'same_jpg_fail': (
        'http://localhost:8000/image.jpg',
        [
            ('Content-Type', 'image/jpg'),
            ('Content-Length', '654'),
        ],
    ),

    'missing_file_suffix': (
        'http://localhost:8000/index',
        [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Length', '164'),
        ],
    ),

    'missing_file_suffix_fail': (
        'http://localhost:8000/index',
        [
            ('Content-Type', 'image/png'),
            ('Content-Length', '164'),
        ],
    ),

    'directory': (
        'http://localhost:8000/foo/', [('Content-Type', 'text/html')]
    ),
}
@pytest.mark.parametrize('testname', TEST_DATA)
def test_kwargs_exclude(testname):
    url_path, headers= TEST_DATA[testname]
    error = testname[-5:] == '_fail'

    if error:
        with pytest.raises(ValueError):
            check_mimetype(url_path, headers)
    else:
        check_mimetype(url_path, headers)


TEST_DATA_DEFAULT = {
    'missing_file_suffix': (
        'http://localhost:8000/index',
        [
            ('Content-Type', 'image/png'),
            ('Content-Length', '164'),
        ],
        'image/png'
    ),

    'missing_file_suffix_fail': (
        'http://localhost:8000/index',
        [
            ('Content-Type', 'text/html'),
            ('Content-Length', '164'),
        ],
        'image/png'
    ),

    'default_ignored': (
        'http://localhost:8000/picture.jpg',
        [
            ('Content-Type', 'image/jpeg'),
            ('Content-Length', '164'),
        ],
        'image/png'
    ),

    'default_ignored_fail': (
        'http://localhost:8000/picture.jpg',
        [
            ('Content-Type', 'image/png'),
            ('Content-Length', '164'),
        ],
        'image/png'
    )
}
@pytest.mark.parametrize('testname', TEST_DATA_DEFAULT)
def test_default_include(testname):
    url_path, headers, default = TEST_DATA_DEFAULT[testname]
    error = testname[-5:] == '_fail'

    if error:
        with pytest.raises(ValueError):
            check_mimetype(url_path, headers, default=default)
    else:
        check_mimetype(url_path, headers, default=default)


def test_missing_file_suffix_get_mimetype():
    def get_mimetype(url_path):
        return ["image/png"]

    check_mimetype(
        'http://localhost:8000/index',
        [
            ('Content-Type', 'image/png'),
            ('Content-Length', '164'),
        ],
        get_mimetype=get_mimetype
    )


def test_get_mimetype_capital_mimetype(monkeypatch):
    def get_mimetype(url_path):
        return ["image/PNG"]

    check_mimetype(
        'http://localhost:8000/image.png',
        [
            ('Content-Type', 'image/png'),
            ('Content-Length', '164'),
        ],
        get_mimetype=get_mimetype
    )


def test_missing_file_suffix_get_mimetype_fail():
    def get_mimetype(url_path):
        return ["image/png"]

    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/index',
            [
                ('Content-Type', 'image/jpeg'),
                ('Content-Length', '164'),
            ],
            get_mimetype=get_mimetype
        )


def test_missing_file_suffix_get_mimetype_fail_default_ignored():
    def get_mimetype(url_path):
        return ["image/bmp"]

    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/index',
            [
                ('Content-Type', 'text/html'),
                ('Content-Length', '164'),
            ],
            default='text/html',
            get_mimetype=get_mimetype,

        )
