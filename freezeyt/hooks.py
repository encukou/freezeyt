from typing import Iterable, Callable, Optional, TYPE_CHECKING
import urllib.parse

from freezeyt.util import parse_absolute_url


if TYPE_CHECKING:
    from freezeyt.freezer import Freezer, Task

class TaskInfo:
    """Public information about a task that's being saved"""
    def __init__(self, task: 'Task'):
        self._task = task
        self._freezer = task.freezer

    def get_a_url(self) -> str:
        """Return a URL of this page

        Note that a page may be reachable via several URLs; this function
        returns an arbitrary one.
        """
        return urllib.parse.urlunsplit(self._task.get_a_url())

    @property
    def path(self) -> str:
        """The relative path the content is saved to"""
        return str(self._task.path)

    @property
    def freeze_info(self) -> 'FreezeInfo':
        """
        A [`FreezeInfo`][freezeyt.FreezeInfo] object corresponding to the
        entire freeze process.
        """

        return self._freezer.freeze_info

    @property
    def exception(self) -> Optional[BaseException]:
        """For failed tasks, the exception raised."""
        aio_task = self._task.asyncio_task
        if aio_task is None:
            return None
        if aio_task.done():
            return aio_task.exception()
        else:
            return None

    @property
    def reasons(self) -> Iterable[str]:
        """A list of strings explaining why the given page was visited.

        Note that as the freezing progresses, new reasons may be added to
        existing tasks.
        """
        return sorted(self._task.reasons)


class FreezeInfo:
    """Public information about a freezer"""

    def __init__(self, freezer: 'Freezer'):
        self._freezer = freezer

    def add_url(self, url: str, reason: Optional[str] = None) -> None:
        """Add the URL to the set of pages to be frozen.

        Args:
            url: The URL to add.

                If that URL was frozen already or is external
                (that is, outside the [prefix][conf-prefix]),
                `add_url` does nothing.

            reason: A note that will be used in error messages as
                the reason why the added URL is being handled.
        """
        self._freezer.add_task(parse_absolute_url(url), reason=reason)

    def add_hook(self, hook_name: str, func: Callable) -> None:
        """Register an additional hook function.

        Args:
            hook_name: Hook name. See [hook docs][conf-hooks] for a list.
            func: Function to call.
        """
        self._freezer.add_hook(hook_name, func)

    @property
    def fail_fast(self) -> bool:
        return self._freezer.fail_fast

    @property
    def total_task_count(self) -> int:
        """Number of pages Freezeyt currently “knows about”.

        This includes pages that are already done plus ones that are
        scheduled to be frozen.
        """
        return sum(
            len(tasks) for tasks in self._freezer.task_collections.values()
        )

    @property
    def done_task_count(self) -> int:
        """The number of pages that are done.

        This includes both pages that were successfully frozen and failed ones.
        """

        # Import TaskStatus here to avoid a circular import
        # (since freezer imports hooks)
        from freezeyt.freezer import TaskStatus
        return (
            len(self._freezer.task_collections[TaskStatus.FAILED])
            + len(self._freezer.task_collections[TaskStatus.DONE])
        )

    @property
    def failed_task_count(self) -> int:
        """The number of pages that failed to freeze."""
        # Import TaskStatus here, see done_task_count
        from freezeyt.freezer import TaskStatus
        return len(self._freezer.task_collections[TaskStatus.FAILED])
