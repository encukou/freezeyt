from typing import Callable, TYPE_CHECKING

from freezeyt.hooks import TaskInfo
from freezeyt.util import urljoin

ActionFunction = Callable[[TaskInfo], str]


def warn(task: TaskInfo) -> str:
    task._freezer.warnings.append(
        f"URL {task.get_a_url()},"
        + f" status code: {task._task.response_status[:3]} was freezed"
    )

    return 'save'


def follow(task: TaskInfo) -> str:
    location = task._task.response_headers['Location']
    location = urljoin(task._task.get_a_url(), location)

    target_task = task._freezer.add_task(
        location,
        external_ok=True,
        reason=f'target of redirect from: {task._task.path}',
    )

    task._task.redirects_to = target_task
    del task._freezer.inprogress_tasks[task._task.path]
    task._freezer.redirecting_tasks[task._task.path] = task._task

    return 'follow'


def ignore(task: TaskInfo) -> str:
    return 'ignore'


def save(task: TaskInfo) -> str:
    return 'save'


def error(task: TaskInfo) -> str:
    return 'error'


if TYPE_CHECKING:
    # Check that the default functions have the proper types
    _: ActionFunction
    _ = warn
    _ = follow
    _ = ignore
    _ = save
    _ = error
