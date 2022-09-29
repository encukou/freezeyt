import traceback
import sys
from subprocess import check_output, CalledProcessError, STDOUT
from textwrap import dedent

import enlighten
import click


class ProgressBarPlugin:
    def __init__(self, freeze_info):
        bar_format = '{percentage:3.0f}%▕{bar}▏{elapsed}, {rate:.2f} pg/s'
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

class GHPagesPlugin:
    def __init__(self, freeze_info):
        success = not freeze_info._freezer.failed_tasks
        base_path = freeze_info._freezer.saver.base_path
        prefix_host = freeze_info._freezer.prefix.host
        if success and base_path.exists():
            with open(str(base_path / "CNAME"), 'w') as f:
                f.write(prefix_host)
            with open(str(base_path / ".nojekyll"), 'w'): 
                pass # only create the empty file
            try:
                sp_params = {"stderr": STDOUT, "shell": True, "cwd": base_path}
                check_output("git init -b gh-pages", **sp_params)
                check_output("git add .", **sp_params)
                check_output('git commit -m "added all freezed files"', **sp_params)
            except CalledProcessError as e:
                print(dedent(f"""
                      Freezing was successful, but a problem occurs during the execution of one of commands for creating git gh-pages branch:
                      command: {e.cmd}
                      captured standard output with error:
                      {e.stdout.decode()}"""))
