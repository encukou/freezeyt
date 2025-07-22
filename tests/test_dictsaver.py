import asyncio
from pathlib import PurePosixPath

from freezeyt.dictsaver import DictSaver

import pytest


@pytest.mark.parametrize('cleanup', (True, False))
@pytest.mark.parametrize('success', (True, False))
def test_empty(success, cleanup):
    saver = DictSaver()
    assert asyncio.run(saver.finish(success, cleanup)) == {}


@pytest.mark.parametrize('cleanup', (True, False))
@pytest.mark.parametrize('success', (True, False))
def test_save_file(success, cleanup):
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('test.txt'), [b'text']))
    assert asyncio.run(saver.finish(success, cleanup)) == {
        'test.txt': b'text',
    }


def test_open_root():
    saver = DictSaver()

    with pytest.raises(IsADirectoryError) as err_info:
        asyncio.run(saver.open_filename(PurePosixPath('')))
    assert str(err_info.value) == '.'

def test_absolute():
    saver = DictSaver()
    with pytest.raises(ValueError):
        asyncio.run(saver.open_filename(PurePosixPath('/')))
    with pytest.raises(ValueError):
        asyncio.run(saver.open_filename(PurePosixPath('/a/b/c')))
    with pytest.raises(ValueError):
        asyncio.run(saver.save_to_filename(PurePosixPath('/'), []))
    with pytest.raises(ValueError):
        asyncio.run(saver.save_to_filename(PurePosixPath('/a/b/c'), []))


def test_open_file():
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('test.txt'), [b'text']))

    file = asyncio.run(saver.open_filename(PurePosixPath('test.txt')))
    assert file.read() == b'text'


def test_open_dir():
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('d/test.txt'), [b'text']))

    with pytest.raises(IsADirectoryError) as err_info:
        asyncio.run(saver.open_filename(PurePosixPath('d')))
    assert str(err_info.value) == 'd'

    with pytest.raises(IsADirectoryError) as err_info:
        asyncio.run(saver.open_filename(PurePosixPath('')))
    assert str(err_info.value) == '.'



def test_open_file_in_file():
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('d/test.txt'), [b'text']))

    with pytest.raises(NotADirectoryError) as err_info:
        asyncio.run(saver.open_filename(PurePosixPath('d/test.txt/file')))
    assert str(err_info.value) == 'd/test.txt'



def test_open_missing_file():
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('d/test.txt'), [b'text']))

    with pytest.raises(FileNotFoundError) as err_info:
        asyncio.run(saver.open_filename(PurePosixPath('d/bad_file')))
    assert str(err_info.value) == 'd/bad_file'


@pytest.mark.parametrize('cleanup', (True, False))
@pytest.mark.parametrize('success', (True, False))
def test_save_iter(success, cleanup):
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('test.txt'), [
        b'text1', b'text2',
    ]))
    asyncio.run(saver.save_to_filename(PurePosixPath('empty.txt'), []))
    assert asyncio.run(saver.finish(success, cleanup)) == {
        'test.txt': b'text1text2',
        'empty.txt': b'',
    }


@pytest.mark.parametrize('cleanup', (True, False))
@pytest.mark.parametrize('success', (True, False))
def test_save_subdir(success, cleanup):
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('a/b/t'), [b'text']))
    assert asyncio.run(saver.finish(success, cleanup)) == {
        'a': {
            'b': {
                't': b'text',
            }
        }
    }


@pytest.mark.parametrize('cleanup', (True, False))
@pytest.mark.parametrize('success', (True, False))
def test_save_many(success, cleanup):
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('a/b/t'), [b'a/b/t']))
    asyncio.run(saver.save_to_filename(PurePosixPath('a/c/t'), [b'a/c/t']))
    asyncio.run(saver.save_to_filename(PurePosixPath('a/t'), [b'a/t']))
    asyncio.run(saver.save_to_filename(PurePosixPath('a/b/c/t'), [b'a/b/c/t']))
    asyncio.run(saver.save_to_filename(PurePosixPath('d/t'), [b'd/t']))
    asyncio.run(saver.save_to_filename(PurePosixPath('t'), [b't']))
    assert asyncio.run(saver.finish(success, cleanup)) == {
        't': b't',
        'a': {
            't': b'a/t',
            'b': {
                't': b'a/b/t',
                'c': {
                    't': b'a/b/c/t',
                },
            },
            'c': {
                't': b'a/c/t',
            },
        },
        'd': {
            't': b'd/t',
        },
    }


@pytest.mark.parametrize('cleanup', (True, False))
@pytest.mark.parametrize('success', (True, False))
def test_overwrite(success, cleanup):
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('test.txt'), [b'orig']))
    asyncio.run(saver.save_to_filename(PurePosixPath('test.txt'), [b'new']))
    assert asyncio.run(saver.finish(success, cleanup)) == {
        'test.txt': b'new',
    }


def test_save_dir_to_file():
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('t'), [b't']))
    with pytest.raises(NotADirectoryError) as err_info:
        asyncio.run(saver.save_to_filename(PurePosixPath('t/x/f'), [b'f']))
    assert str(err_info.value) == 't/x'


def test_save_file_to_dir():
    saver = DictSaver()
    asyncio.run(saver.save_to_filename(PurePosixPath('t/f'), [b'f']))
    with pytest.raises(IsADirectoryError):
        asyncio.run(saver.save_to_filename(PurePosixPath('t'), [b't']))
