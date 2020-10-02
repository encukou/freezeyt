import pytest

from freezeyt.freezing import check_mimetype

def test_normal_html():
    check_mimetype(
        '/tmp/index.html',
        [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', '164'),
        ]
    )

def test_diff_type_jpg_png_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            '/tmp/image.jpg',
            [
                ('Content-Type', 'image/png'),
                ('Content-Length', '654'),
            ],
        )


def test_missing_content_type():
    with pytest.raises(ValueError):
        check_mimetype(
            '/tmp/index.html',
            [
                ('Content-Length', '164'),
            ]
        )


def test_case_insensitive_content_type():
        check_mimetype(
            '/tmp/index.html',
            [
                ('Content-Type', 'TEXT/HTML; charset=utf-8'),
                ('Content-Length', '164'),
            ]
        )


def test_case_insensitive_file():
        check_mimetype(
            '/tmp/index.HTML',
            [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', '164'),
            ]
        )


def test_case_insensitive_headers_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            '/tmp/image.jpg',
            [
                ('CONTENT-TYPE', 'IMAGE/PNG'),
                ('Content-Length', '654'),
            ],
        )


def test_case_insensitive_headers():
    check_mimetype(
        '/tmp/image.jpg',
        [
            ('coNtENT-TypE', 'IMAgE/JpEG'),
            ('Content-Length', '654'),
        ],
    )


def test_same_jpg_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            '/tmp/image.jpg',
            [
                ('Content-Type', 'image/jpg'),
                ('Content-Length', '654'),
            ],
        )
