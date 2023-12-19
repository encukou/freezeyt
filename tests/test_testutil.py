from pathlib import PurePosixPath
from typing import NoReturn

import pytest

from freezeyt import MultiError
from freezeyt.freezer import Task
from freezeyt.hooks import TaskInfo
from freezeyt.compat import asyncio_run, asyncio_create_task

from testutil import assert_dirs_same, FIXTURES_PATH
from testutil import raises_multierror_with_one_exception

DIRS_SAME_FIXTURES = FIXTURES_PATH / 'dirs_same'
DIRS_SAME_CASES = [p.name for p in DIRS_SAME_FIXTURES.iterdir()]


@pytest.mark.parametrize('dir_name', DIRS_SAME_CASES)
def test_assert_dirs_same(dir_name):
    path = DIRS_SAME_FIXTURES / dir_name

    if path.name in ('testdir', 'same'):
        assert_dirs_same(path, DIRS_SAME_FIXTURES / 'testdir')
    else:
        with pytest.raises(AssertionError):
            assert_dirs_same(path, DIRS_SAME_FIXTURES / 'testdir')


def test_files_with_same_signature(tmp_path):
    dir1 = tmp_path / 'dir1'
    dir2 = tmp_path / 'dir2'

    dir1.mkdir()
    dir2.mkdir()

    path1 = dir1 / 'file.txt'
    path2 = dir2 / 'file.txt'

    path1.write_text('A')
    path2.write_text('B')

    with pytest.raises(AssertionError):
        assert_dirs_same(dir1, dir2)


async def create_failing_task() -> Task:
    """Create a fake freezeyt task that failed with an AssertionError"""
    async def fail() -> NoReturn:
        """coroutine that fails"""
        raise AssertionError()
    # Create an asyncio task
    asyncio_task = asyncio_create_task(fail(), name='test')
    # Wait for it to be done (catching the AssertionError)
    with pytest.raises(AssertionError):
        await asyncio_task
    # Wrap it in a fake freezeyt Task
    return Task(
        path=PurePosixPath('test'),
        urls=set(),
        freezer=None,  # type: ignore[arg-type]
        asyncio_task=asyncio_task,
    )


def test_raises_multierror():
    """raises_multierror_with_one_exception exposes correct exception info
    """
    dummy_task = asyncio_run(create_failing_task())

    with raises_multierror_with_one_exception(AssertionError) as e:
        raise MultiError([dummy_task])
    assert e.type == AssertionError
    assert isinstance(e.value, AssertionError)
    assert isinstance(e.freezeyt_task, TaskInfo)
    assert e.freezeyt_task._task == dummy_task


def test_raises_multierror_no_exception():
    """raises_multierror_with_one_exception fails if no error occurred"""
    with pytest.raises(BaseException):
        with raises_multierror_with_one_exception(AssertionError):
            pass


def test_raises_multierror_different_exception():
    """raises_multierror_with_one_exception fails if MultiError has bad error
    """
    dummy_task = asyncio_run(create_failing_task())

    with pytest.raises(BaseException):
        with raises_multierror_with_one_exception(TypeError):
            raise MultiError([dummy_task])


def test_raises_multierror_nonmulti_error():
    """raises_multierror_with_one_exception fails if non-MultiError if raised
    """

    with pytest.raises(BaseException):
        with raises_multierror_with_one_exception(TypeError):
            raise TypeError()


def test_raises_multierror_0_errors():
    """
    raises_multierror_with_one_exception fails if MultiError has 0 exceptions
    """
    with pytest.raises(BaseException):
        with raises_multierror_with_one_exception(AssertionError):
            raise MultiError([])


def test_raises_multierror_2_errors():
    """
    raises_multierror_with_one_exception fails if MultiError has too many excs
    """
    dummy_task1 = asyncio_run(create_failing_task())
    dummy_task2 = asyncio_run(create_failing_task())

    with pytest.raises(BaseException):
        with raises_multierror_with_one_exception(AssertionError):
            raise MultiError([dummy_task1, dummy_task2])
