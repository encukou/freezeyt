import pytest
from pathlib import Path

from freezeyt.extra_files import get_extra_files
from freezeyt import freeze

from testutil import FIXTURES_PATH, context_for_test

IMAGE_BYTES = b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\x08\0\0\0\x08\x08\x04\0\0\0n\x06v\0\0\0\0#IDAT\x08\xd7cd``\xf8\xcf\x80\0\x8c\xa8\\ \x8f\tB!\x91D\xab\xf8\x8f\x10D\xd3\xc2\x88n-\0\x0e\x1b\x0f\xf9LT9_\0\0\0\0IEND\xaeB`\x82'

def test_simple():
    config = {
        'extra_files': {
            'foo': 'abc',
        }
    }
    assert list(get_extra_files(config)) == [('foo', 'content', b'abc')]


EXTRA_FILE_SLASH = {
    'url_part': {'url_part': b'a'},
    '/url_part': {'url_part': b'a'},
    'url_part/': {'url_part': {'index.html': b'a'}},
    '/url_part/': {'url_part': {'index.html': b'a'}},
    '/url_part//': {'url_part': {'index.html': b'a'}},
    '//url_part/': {'url_part': {'index.html': b'a'}},
    '/path_to//file': {'path_to': {'file': b'a'}},
    'path_to///file': {'path_to': {'file': b'a'}},
    '/part1///part2/': {'part1': {'part2': {'index.html': b'a'}}},
    '/http/https/': {'http': {'https': {'index.html': b'a'}}},
    r'/http\https/': {'http': {'https': {'index.html': b'a'}}},
}
@pytest.mark.parametrize('test_case', EXTRA_FILE_SLASH)
def test_slashes(test_case):
    extra_file = {test_case: 'a'}
    expected = EXTRA_FILE_SLASH[test_case]
    config = {
        'extra_files': extra_file,
        'output': {'type': 'dict'},
    }

    with context_for_test('app_simple') as module:
        result = freeze(module.app, config)

    assert result is not None

    # pop to simplify syntax of expected dict
    # index.html is root page for app_simple, not useful for this test
    result.pop('index.html')

    assert result == expected

EXTRA_FILE_DOT = {
    ':': {':': b'a'},
    ':/': {':': {'index.html': b'a'}},
    '.nojekyll': {'.nojekyll': b'a'},
    '/.nojekyll': {'.nojekyll': b'a'},
    '/info.txt': {'info.txt': b'a'},
    '/./a/./a.b.': {'a': {'a.b.': b'a'}},
    '/./a/./a.b./.': {'a': {'a.b.': {'index.html': b'a'}}},
    './a/./a.b./.': {'a': {'a.b.': {'index.html': b'a'}}},
    './a/./a.b././': {'a': {'a.b.': {'index.html': b'a'}}},
    '/./././a.b./.': {'a.b.': {'index.html': b'a'}},
    'a..b/a../b..': {'a..b': {'a..': {'b..': b'a'}}},
    'a..b/a../..b/': {'a..b': {'a..': {'..b': {'index.html': b'a'}}}},
    '/..b../': {'..b..': {'index.html': b'a'}},
    '/..b..': {'..b..': b'a'},
    # http: without leading forward slash become absolute url instead of url part
    'http:': {'http:': b'a'},
    '/http:': {'http:': b'a'},
    '/http:/': {'http:': {'index.html': b'a'}},
    '/https:/': {'https:': {'index.html': b'a'}},
    '/https://': {'https:': {'index.html': b'a'}},
    '/http:/https:/': {'http:': {'https:': {'index.html': b'a'}}},
    '/http:/foo/': {'http:': {'foo': {'index.html': b'a'}}},
}
@pytest.mark.parametrize('test_case', EXTRA_FILE_DOT)
def test_dots(test_case):
    extra_file = {test_case: 'a'}
    expected = EXTRA_FILE_DOT[test_case]
    config = {
        'extra_files': extra_file,
        'output': {'type': 'dict'},
    }

    with context_for_test('app_simple') as module:
        result = freeze(module.app, config)

    assert result is not None

    # pop to simplify syntax of expected dict
    # index.html is root page for app_simple, not useful for this test
    result.pop('index.html')

    assert result == expected


EXTRA_FILE_QUOTED = {
    '%C3%A1/':  {'á': {'index.html': b'a'}},
    'á/':       {'á': {'index.html': b'a'}},
    '/a%5cb/':  {'a\\b': {'index.html': b'a'}},
}
@pytest.mark.parametrize('test_case', EXTRA_FILE_QUOTED)
def test_quoted_url_path(test_case):
    extra_file = {test_case: 'a'}
    expected = EXTRA_FILE_QUOTED[test_case]
    config = {
        'extra_files': extra_file,
        'output': {'type': 'dict'},
    }

    with context_for_test('app_simple') as module:
        result = freeze(module.app, config)

    assert result is not None

    # pop to simplify syntax of expected dict
    # index.html is root page for app_simple, not useful for this test
    result.pop('index.html')

    assert result == expected

EXTRA_FILE_WITH_PREFIX = {
    # url_part - from configuration: expected url_part - after clean
    ':':                ':',
    ':/':               ':/',
    '.nojekyll':        '.nojekyll',
    '/.nojekyll':       '.nojekyll',
    'http:/info.txt':   'http:/info.txt',
    '/./a/./a.b.':      'a/a.b.',
    '/./a/./a.b./.':    'a/a.b./',
    './a/./a.b./.':     'a/a.b./',
    './a/./a.b././':    'a/a.b./',
    '/./././a.b./.':    'a.b./',
    'a..b/a../b..':     'a..b/a../b..',
    'a..b/a../..b/':    'a..b/a../..b/',
    '/..b../':          '..b../',
    '/..b..':           '..b..',
    'http':             'http',
    '/a%5cb/':          'a\\b/',
    '%C3%A1/':          'á/',
    'á/':               'á/',
    # http: without leading forward slash alter prefix by werkzeug.url_parse(<prefix>).join("http:")
    # http: become the protocol of prefix instead url path
    'http:':            'http:',
    '/http:':           'http:',
    '/http:/':          'http:/',
    '/https:/':         'https:/',
    '/https://':        'https:/',
    '/http:/https/':    'http:/https/',
    r'/http\https/':    'http/https/',
}
@pytest.mark.parametrize('url_part', EXTRA_FILE_WITH_PREFIX)
@pytest.mark.parametrize('prefix', ('https://example.com:443/freezeyt/', 'https://example.com:443/'))
def test_join_with_prefix(url_part, prefix):
    recorded_tasks = {}

    def record_page(task_info):
        recorded_tasks[task_info.get_a_url()] = task_info

    extra_file = {url_part: 'a'}

    config = {
        'prefix': prefix,
        'extra_files': extra_file,
        'output': {'type': 'dict'},
        'hooks': {'page_frozen': [record_page]},
    }

    with context_for_test('app_simple') as module:
        freeze(module.app, config)

    expected = [
        config['prefix'],
        config['prefix'] + EXTRA_FILE_WITH_PREFIX[url_part],
    ]

    assert sorted(recorded_tasks) == expected


EXTRA_FILE_INVALID = (
    '../a/b.txt',
    '/a/../b.txt',
    '/a/b/..',
)
@pytest.mark.parametrize('url_path', EXTRA_FILE_INVALID)
def test_invalid_url_part(url_path):
    extra_file = {url_path: 'a'}
    config = {
        'extra_files': extra_file,
        'output': {'type': 'dict'},
    }

    with context_for_test('app_simple') as module:
        with pytest.raises(ValueError):
            freeze(module.app, config)


def test_relative_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath('somefile.txt').write_bytes(b'hello world')
    config = {
        'output': {'type': 'dict'},
        'extra_files': {
            'somefile': {
                'copy_from': 'somefile.txt',
            }
        }
    }
    with context_for_test('app_simple') as module:
        result = freeze(module.app, config)

    result.pop('index.html')
    assert result == {'somefile': b'hello world'}


def test_content():
    config = {
        'extra_files': {
            'str.txt': 'ábč',
            'bytes.dat': b'def',
            'base64.dat': {'base64': 'Z2hp'},
            'copied.png': {
                'copy_from': FIXTURES_PATH / 'app_with_extra_files/smile2.png'
            },
            'directory': {
                'copy_from': 'some/dir',
            },
        }
    }
    assert sorted(get_extra_files(config)) == sorted([
        ('str.txt', 'content', 'ábč'.encode()),
        ('bytes.dat', 'content', b'def'),
        ('base64.dat', 'content', b'ghi'),
        ('copied.png', 'path', FIXTURES_PATH / 'app_with_extra_files/smile2.png'),
        ('directory', 'path', Path.cwd() / 'some/dir'),
    ])
