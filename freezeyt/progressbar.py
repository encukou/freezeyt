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

class LogPlugin:
    def __init__(self, freeze_info):
        freeze_info.add_hook('page_frozen', self.page_frozen)

    def page_frozen(self, task_info):
        total = task_info.freeze_info.total_task_count
        count = task_info.freeze_info.done_task_count
        progress = count / total
        print(
            f'[{count:{len(str(total))}d}/{total}, ~{progress:3.0%}]',
            task_info.path,
        )
