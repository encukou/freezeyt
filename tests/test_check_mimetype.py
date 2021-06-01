import pytest

from freezeyt.freezer import check_mimetype

def test_normal_html():
    check_mimetype(
        'http://localhost:8000/index.html',
        [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', '164'),
        ]
    )

def test_diff_type_jpg_png_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/image.jpg',
            [
                ('Content-Type', 'image/png'),
                ('Content-Length', '654'),
            ],
        )


def test_missing_content_type():
    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/index.html',
            [
                ('Content-Length', '164'),
            ]
        )


def test_case_insensitive_content_type():
        check_mimetype(
            'http://localhost:8000/index.html',
            [
                ('Content-Type', 'TEXT/HTML; charset=utf-8'),
                ('Content-Length', '164'),
            ]
        )


def test_case_insensitive_file():
        check_mimetype(
            'http://localhost:8000/index.HTML',
            [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', '164'),
            ]
        )


def test_case_insensitive_headers_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/image.jpg',
            [
                ('CONTENT-TYPE', 'IMAGE/PNG'),
                ('Content-Length', '654'),
            ],
        )


def test_case_insensitive_headers():
    check_mimetype(
        'http://localhost:8000/image.jpg',
        [
            ('coNtENT-TypE', 'IMAgE/JpEG'),
            ('Content-Length', '654'),
        ],
    )


def test_same_jpg_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/image.jpg',
            [
                ('Content-Type', 'image/jpg'),
                ('Content-Length', '654'),
            ],
        )


def test_missing_file_suffix():
    check_mimetype(
        'http://localhost:8000/index',
        [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Length', '164'),
        ]
    )

def test_missing_file_suffix_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/index',
            [
                ('Content-Type', 'image/png'),
                ('Content-Length', '164'),
            ]
        )

def test_directory():
    check_mimetype(
        'http://localhost:8000/foo/',
        [
            ('Content-Type', 'text/html'),
        ]
    )


def test_missing_file_default():
    check_mimetype(
        'http://localhost:8000/index',
        [
            ('Content-Type', 'image/png'),
            ('Content-Length', '164'),
        ],
        default='image/png'
    )


def test_default_ignored():
    check_mimetype(
        'http://localhost:8000/picture.jpg',
        [
            ('Content-Type', 'image/jpeg'),
            ('Content-Length', '164'),
        ],
        default='image/png'
    )


def test_missing_file_default_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/index',
            [
                ('Content-Type', 'text/html'),
                ('Content-Length', '164'),
            ],
            default='image/png'
        )


def test_default_ignored_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            'http://localhost:8000/picture.jpg',
            [
                ('Content-Type', 'image/png'),
                ('Content-Length', '164'),
            ],
            default='image/png'
        )
