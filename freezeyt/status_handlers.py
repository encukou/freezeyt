from freezeyt.freezer import IsARedirect, IgnorePage
from freezeyt.hooks import TaskInfo
from freezeyt.util import UnexpectedStatus, add_port


def warn(status: str, task: TaskInfo) -> None:
    print(
        f"WARNING: URL {task.get_a_url()}, status code: {status} was freezed"
    )


def follow(status: str, task: TaskInfo) -> None:
    try:
        location = task._task.response_headers['Location']
    except KeyError:
        raise UnexpectedStatus(task.get_a_url(), status, task._task.reasons)

    location = add_port(task._task.get_a_url().join(location))
    target_task = task._freezer.add_task(
        location,
        external_ok=True,
        reason=f'target of redirect from {task._task.get_a_url()}',
    )
    task._task.redirects_to = target_task
    task._freezer.redirecting_tasks[task._task.path] = task._task
    raise IsARedirect()


def ignore(status: str, task: TaskInfo) -> None:
    raise IgnorePage()


def save(status: str, task: TaskInfo) -> str:
    return status


def error(status: str, task: TaskInfo) -> None:
    raise UnexpectedStatus(task.get_a_url(), status, task._task.reasons)
