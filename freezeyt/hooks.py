from freezeyt.util import parse_absolute_url

class TaskInfo:
    """Public information about a task that's being saved"""
    def __init__(self, task, freezer):
        self._task = task
        self._freezer = freezer

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


class FreezeInfo:
    def __init__(self, freezer):
        self._freezer = freezer

    def add_url(self, url):
        self._freezer.add_task(parse_absolute_url(url))
