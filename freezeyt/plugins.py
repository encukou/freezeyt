import traceback
import sys
from subprocess import check_output, CalledProcessError, STDOUT
from textwrap import dedent
from typing import List

import enlighten
import click

from freezeyt.hooks import FreezeInfo, TaskInfo
from freezeyt.filesaver import FileSaver

class GitCommandError(ValueError):
    """An exception occurred while executing git commands."""

class ProgressBarPlugin:
    bar_format = '{percentage:3.0f}%▕{bar}▏{elapsed}, {rate:.2f} pg/s'
    def __init__(self, freeze_info: FreezeInfo):
        self.manager = enlighten.get_manager()
        self.counter = self.manager.counter(
            total=100, color='red', bar_format=self.bar_format)
        self.failure_counter = self.counter
        self.success_counter = self.counter.add_subcounter('cyan')
        freeze_info.add_hook('page_frozen', self.update_bar)
        freeze_info.add_hook('page_failed', self.update_bar)

    def update_bar(self, task_info: TaskInfo) -> None:
        self.counter.total = task_info.freeze_info.total_task_count
        self.counter.count = task_info.freeze_info.done_task_count
        self.success_counter.count = (
            task_info.freeze_info.done_task_count
            - task_info.freeze_info.failed_task_count
        )
        self.counter.update(0)

class LogPlugin:
    def __init__(self, freeze_info: FreezeInfo):
        freeze_info.add_hook('page_frozen', self.page_frozen)
        freeze_info.add_hook('page_failed', self.page_failed)

    def _summary(self, freeze_info: FreezeInfo) -> str:
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

    def page_frozen(self, task_info: TaskInfo) -> None:
        summary = click.style(self._summary(task_info.freeze_info), fg='cyan')
        click.echo(f'{summary} {task_info.path}', file=sys.stderr)

    def page_failed(self, task_info: TaskInfo) -> None:
        summary = click.style(self._summary(task_info.freeze_info), fg='red')
        click.echo(f'{summary} ERROR in {task_info.path}', file=sys.stderr)
        exc = task_info.exception
        assert exc is not None
        if not task_info._freezer.freeze_info.fail_fast:
            traceback.print_exception(type(exc), exc, exc.__traceback__)

class GHPagesPlugin:
    def __init__(self, freeze_info: FreezeInfo):
        if freeze_info._freezer.prefix.path != "/":
            raise ValueError("When using the Github Pages plugin, you can't specify a path in the prefix, so github can't handle it.")
        if not isinstance(freeze_info._freezer.saver, FileSaver):
            raise ValueError("When using the Github Pages plugin, you must save to a directory.")
        self.base_path = freeze_info._freezer.saver.base_path
        hostname = freeze_info._freezer.prefix.hostname
        assert hostname is not None
        self.prefix_host = hostname
        freeze_info.add_hook('success', self.github_pages)

    def github_pages(self, freeze_info: FreezeInfo) -> None:
        if self.base_path.exists():
            (self.base_path / "CNAME").write_text(self.prefix_host)
            (self.base_path / ".nojekyll").write_text("")
            def run_git(command: List[str]) -> None:
                check_output(
                    command,
                    stderr=STDOUT,
                    cwd=self.base_path,
                    env={
                        "GIT_CONFIG_NOSYSTEM": "1",
                        "GIT_AUTHOR_NAME": "gh_pages",
                        "GIT_AUTHOR_EMAIL": "gh@mail.invalid",
                        "GIT_COMMITTER_NAME": "gh_pages",
                        "GIT_COMMITTER_EMAIL": "gh@mail.invalid",
                    },
                )
            try:
                run_git(["git", "init", "-b", "gh-pages"])
                run_git(["git", "add", "."])
                run_git(["git", "commit", "-m", "added all freezed files"])
            except CalledProcessError as e:
                raise GitCommandError(f"""
                      Freezing was successful, but a problem occurs during the execution of one of commands for creating git gh-pages branch:
                      command: {e.cmd}
                      captured standard output with error:
                      {e.stdout.decode()}""")
            else:
                print(dedent("""
                      The gh-pages git branch has been successfully created,
                      you can work with it in the output directory.
                      Check the page https://github.com/encukou/freezeyt#github-pages-plugin for tips on how to do this."""))
