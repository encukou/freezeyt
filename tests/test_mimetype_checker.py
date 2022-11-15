import pytest

from freezeyt.mimetype_check import MimetypeChecker


def test_simple_check():
    checker = MimetypeChecker({})
    checker.check('smile.png', [('Content-Type', 'image/png')])
    with pytest.raises(ValueError):
        checker.check('smile.png', [('Content-Type', 'bad')])


def test_guess_mimetype():
    checker = MimetypeChecker({})
    assert checker.guess_mimetype('smile.png') == 'image/png'
    assert checker.guess_mimetype('smile') == 'application/octet-stream'


def test_guess_mimetype_with_default():
    checker = MimetypeChecker({'default_mimetype': 'text/plain'})
    assert checker.guess_mimetype('smile.png') == 'image/png'
    assert checker.guess_mimetype('smile') == 'text/plain'
