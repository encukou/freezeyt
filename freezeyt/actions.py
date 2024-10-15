from typing import Callable, TYPE_CHECKING

from freezeyt.hooks import TaskInfo
from freezeyt.util import urljoin, TaskStatus

ActionFunction = Callable[[TaskInfo], str]


def warn(task: TaskInfo) -> str:
    """Save the content, but send warn message to stdout."""
    url = task.get_a_url()
    response_status = task._task.response_status
    if response_status is None:
        raise ValueError(
            f'warn() called on {url} which is not being saved yet')
    task._freezer.warnings.append(
        f"URL {url},"
        + f" status code: {response_status[:3]} was freezed"
    )

    return 'save'


def follow(task: TaskInfo) -> str:
    """Save content from the redirected location.

    This requires a Location header, which is usually added for redirects.
    Redirects to external pages are not supported.
    """
    url = task._task.get_a_url()
    response_headers = task._task.response_headers
    if response_headers is None:
        raise ValueError(
            f'follow() called on {url} which is not being saved yet')
    location = urljoin(url, response_headers['Location'])

    target_task = task._freezer.add_task(
        location,
        external_ok=True,
        reason=f'target of redirect from: {task._task.path}',
    )

    task._task.redirects_to = target_task
    task._task.update_status(TaskStatus.IN_PROGRESS, TaskStatus.REDIRECTING)

    return 'follow'


def ignore(task: TaskInfo) -> str:
    """Do not save any content for the page."""
    return 'ignore'


def save(task: TaskInfo) -> str:
    """Save the body of the page."""
    return 'save'


def error(task: TaskInfo) -> str:
    """Raise an exception."""
    return 'error'


if TYPE_CHECKING:
    # Check that the default functions have the proper types
    _: ActionFunction
    _ = warn
    _ = follow
    _ = ignore
    _ = save
    _ = error
