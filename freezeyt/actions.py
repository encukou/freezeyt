from typing import Callable, TYPE_CHECKING

from freezeyt.hooks import TaskInfo
from freezeyt.util import TaskStatus, ExternalURLError

ActionFunction = Callable[[TaskInfo], str]


_ACTIONS = {}

def register(func):
    _ACTIONS[func.__name__] = func
    return func


@register
def warn(task: TaskInfo) -> str:
    url = task.get_a_url()
    response = task._task.response
    if response is None:
        raise ValueError(
            f'warn() called on {url} which is not being saved yet')
    task._freezer.warnings.append(
        f"URL {url},"
        + f" status code: {response.status[:3]} was freezed"
    )

    return 'save'


@register
def follow(task: TaskInfo) -> str:
    url = task._task.get_a_url()
    response = task._task.response
    if response is None:
        raise ValueError(
            f'follow() called on {url} which is not being saved yet')
    try:
        location = url.join(response.headers['Location'])
    except ExternalURLError:
        raise NotImplementedError(
            'Redirects to external pages are not supported',
        )

    target_task = task._freezer.add_task(
        location,
        reason=f'target of redirect from: {task._task.path}',
    )

    task._task.redirects_to = target_task
    task._task.update_status(TaskStatus.IN_PROGRESS, TaskStatus.REDIRECTING)

    return 'follow'


@register
def ignore(task: TaskInfo) -> str:
    return 'ignore'


@register
def save(task: TaskInfo) -> str:
    return 'save'


@register
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
