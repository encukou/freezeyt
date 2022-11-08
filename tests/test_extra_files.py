from freezeyt.extra_files import get_extra_files

from testutil import FIXTURES_PATH

IMAGE_BYTES = b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\x08\0\0\0\x08\x08\x04\0\0\0n\x06v\0\0\0\0#IDAT\x08\xd7cd``\xf8\xcf\x80\0\x8c\xa8\\ \x8f\tB!\x91D\xab\xf8\x8f\x10D\xd3\xc2\x88n-\0\x0e\x1b\x0f\xf9LT9_\0\0\0\0IEND\xaeB`\x82'

def test_simple():
    config = {
        'extra_files': {
            'foo': 'abc',
        }
    }
    assert dict(get_extra_files(config)) == {'foo': b'abc'}

def test_content():
    config = {
        'extra_files': {
            'str': 'ábč',
            'bytes': b'def',
            'base64': {'base64': 'Z2hp'},
            'copied': {
                'copy_from': FIXTURES_PATH / 'app_with_extra_files/smile2.png'
            },
        }
    }
    assert dict(get_extra_files(config)) == {
        'str': 'ábč'.encode(),
        'bytes': b'def',
        'base64': b'ghi',
        'copied': IMAGE_BYTES,
    }

def test_tree():
    config = {
        'extra_files': {
            'tree': {
                'copy_from': FIXTURES_PATH / 'app_static_tree/static_dir'
            },
        }
    }
    result = dict(get_extra_files(config))
    assert set(result) == {
        'tree/subdir/static.txt',
        'tree/smile.png',
        'tree/static.txt',
    }
    assert result['tree/static.txt'] == b'Hello\n'
