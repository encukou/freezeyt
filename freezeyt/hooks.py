from typing import Iterable, Callable, Optional, TYPE_CHECKING

from freezeyt.urls import AppURL


if TYPE_CHECKING:
    from freezeyt.freezer import Freezer, Task

class TaskInfo:
    """Public information about a task that's being saved"""
    def __init__(self, task: 'Task'):
        self._task = task
        self._freezer = task.freezer

    def get_a_url(self) -> str:
        """Return a URL of this page"""
        return str(self._task.get_a_url())

    @property
    def path(self) -> str:
        """The relative path the content is saved to"""
        return str(self._task.path)

    @property
    def freeze_info(self) -> 'FreezeInfo':
        return self._freezer.freeze_info

    @property
    def exception(self) -> Optional[BaseException]:
        return self._task.exception

    @property
    def reasons(self) -> Iterable[str]:
        """A list of strings explaining why the given page was visited.

        New entries may be added as the freezing goes on.
        """
        return sorted(self._task.reasons)


class FreezeInfo:
    """Public information about a freezer"""

    def __init__(self, freezer: 'Freezer'):
        self._freezer = freezer

    def add_url(self, url: str, reason: Optional[str] = None) -> None:
        self._freezer.add_task(AppURL(url, self._freezer.prefix), reason=reason)

    def add_hook(self, hook_name: str, func: Callable) -> None:
        self._freezer.add_hook(hook_name, func)

    @property
    def fail_fast(self) -> bool:
        return self._freezer.fail_fast

    @property
    def total_task_count(self) -> int:
        return sum(
            len(tasks) for tasks in self._freezer.task_collections.values()
        )

    @property
    def done_task_count(self) -> int:
        # Import TaskStatus here to avoid a circular import
        # (since freezer imports hooks)
        from freezeyt.freezer import TaskStatus
        return (
            len(self._freezer.task_collections[TaskStatus.FAILED])
            + len(self._freezer.task_collections[TaskStatus.DONE])
        )

    @property
    def failed_task_count(self) -> int:
        # Import TaskStatus here, see done_task_count
        from freezeyt.freezer import TaskStatus
        return len(self._freezer.task_collections[TaskStatus.FAILED])
