from freezeyt.hooks import TaskInfo
from freezeyt.util import add_port


def warn(task: TaskInfo) -> str:
    print(
        f"WARNING: URL {task.get_a_url()},"
        + f" status code: {task._task.response_status[:3]} was freezed"
    )

    return 'save'


def follow(task: TaskInfo) -> str:
    location = task._task.response_headers['Location']
    location = add_port(task._task.get_a_url().join(location))

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
