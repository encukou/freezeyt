from freezeyt.encoding import decode_input_path, encode_wsgi_path
from freezeyt.encoding import encode_file_path

def test_decode_input_path_ascii():
    assert decode_input_path('/ahoj') == '/ahoj'


def test_decode_input_path_unicode():
    assert decode_input_path('/čau/☺フ') == '/čau/☺フ'


def test_decode_input_path_percent():
    assert decode_input_path('/%C4%8Dau') == '/čau'


def test_decode_input_path_surrogateescape():
    assert decode_input_path('/%8Dau') == '/\udc8dau'


def test_encode_wsgi_path_ascii():
    assert encode_wsgi_path('/ahoj') == '/ahoj'


def test_encode_wsgi_path_unicode():
    expected = '/\xc4\x8dau/\xe2\x98\xba\xe3\x83\x95'
    assert encode_wsgi_path('/čau/☺フ') == expected


def test_encode_wsgi_path_surrogateescape():
    assert encode_wsgi_path('/\udc8dau') == '/\x8Dau'


def test_encode_file_path_ascii():
    assert encode_file_path('/ahoj') == '/ahoj'


def test_encode_file_path_unicode():
    assert encode_file_path('/čau/☺フ') == '/čau/☺フ'


def test_encode_file_path_surrogateescape():
    assert encode_file_path('/\udc8dau') == '/\udc8dau'
