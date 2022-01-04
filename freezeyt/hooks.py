from typing import Iterable

from freezeyt.util import parse_absolute_url

class TaskInfo:
    """Public information about a task that's being saved"""
    def __init__(self, task):
        self._task = task
        self._freezer = task.freezer

    def get_a_url(self):
        """Return a URL of this page"""
        return self._task.get_a_url().to_url()

    @property
    def path(self):
        """The relative path the content is saved to"""
        return str(self._task.path)

    @property
    def freeze_info(self):
        return self._freezer.freeze_info

    @property
    def exception(self):
        if self._task.asyncio_task.done():
            return self._task.asyncio_task.exception()
        else:
            return None

    @property
    def reasons(self) -> Iterable[str]:
        """A list of strings explaining why the given page was visited.

        New entries may be added as the freezing goes on.
        """
        return sorted(self._task.reasons)


class FreezeInfo:
    def __init__(self, freezer):
        self._freezer = freezer

    def add_url(self, url, reason=None):
        self._freezer.add_task(parse_absolute_url(url), reason=reason)

    def add_hook(self, hook_name, func):
        self._freezer.add_hook(hook_name, func)

    @property
    def total_task_count(self):
        return sum(len(tasks) for tasks in self._freezer.task_queues.values())

    @property
    def done_task_count(self):
        # Import TaskStatus here to avoid a circular import
        # (since freezer imports hooks)
        from freezeyt.freezer import TaskStatus
        return (
            len(self._freezer.task_queues[TaskStatus.FAILED])
            + len(self._freezer.task_queues[TaskStatus.DONE])
        )

    @property
    def failed_task_count(self):
        # Import TaskStatus here, see done_task_count
        from freezeyt.freezer import TaskStatus
        return len(self._freezer.task_queues[TaskStatus.FAILED])
