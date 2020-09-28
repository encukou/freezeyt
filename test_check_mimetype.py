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

def test_png_fail():
    with pytest.raises(ValueError):
        check_mimetype(
            '/tmp/image.jpg',
            [
                ('Content-Type', 'image/png'), ('Content-Length', '654'),
            ],
        )
