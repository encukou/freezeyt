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
