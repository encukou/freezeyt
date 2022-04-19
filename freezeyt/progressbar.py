import traceback
import sys

import enlighten
import click

bar_format = '{percentage:3.0f}%▕{bar}▏{elapsed}, {rate:.2f} pg/s'

class ProgressBarPlugin:
    def __init__(self, freeze_info):
        self.manager = enlighten.get_manager()
        self.counter = self.manager.counter(
            total=100, color='red', bar_format=bar_format)
        self.failure_counter = self.counter
        self.success_counter = self.counter.add_subcounter('cyan')
        freeze_info.add_hook('page_frozen', self.update_bar)
        freeze_info.add_hook('page_failed', self.update_bar)

    def update_bar(self, task_info):
        self.counter.total = task_info.freeze_info.total_task_count
        self.counter.count = task_info.freeze_info.done_task_count
        self.success_counter.count = (
            task_info.freeze_info.done_task_count
            - task_info.freeze_info.failed_task_count
        )
        self.counter.update(0)

class LogPlugin:
    def __init__(self, freeze_info):
        freeze_info.add_hook('page_frozen', self.page_frozen)
        freeze_info.add_hook('page_failed', self.page_failed)

    def _summary(self, freeze_info):
        total = freeze_info.total_task_count
        failed = freeze_info.failed_task_count
        done = freeze_info.done_task_count
        progress = done / total
        result = [
            f'[{done:{len(str(total))}d}/{total}, ~{progress:3.0%}'
        ]
        if failed:
            result.append(f', {failed} errors')
        result.append(']')
        return ''.join(result)

    def page_frozen(self, task_info):
        summary = click.style(self._summary(task_info.freeze_info), fg='cyan')
        click.echo(f'{summary} {task_info.path}', file=sys.stderr)

    def page_failed(self, task_info):
        summary = click.style(self._summary(task_info.freeze_info), fg='red')
        click.echo(f'{summary} ERROR in {task_info.path}', file=sys.stderr)
        exc = task_info.exception
        traceback.print_exception(type(exc), exc, exc.__traceback__)

