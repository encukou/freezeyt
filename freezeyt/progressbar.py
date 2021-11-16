import enlighten

bar_format = '{count:{len_total}d}/{total:d} |{bar}|{percentage:3.0f}% [{elapsed}, {rate:.2f} pg/s]'

class ProgressBarPlugin:
    def __init__(self, freeze_info):
        self.manager = enlighten.get_manager()
        self.counter = self.manager.counter(
            total=100, color='cyan', bar_format=bar_format)
        freeze_info.add_hook('page_frozen', self.page_frozen)

    def page_frozen(self, task_info):
        self.counter.total = task_info.freeze_info.total_task_count
        self.counter.count = task_info.freeze_info.done_task_count
        self.counter.update(0)
