import shutil
from subprocess import check_output, CalledProcessError, STDOUT
from textwrap import dedent

from . import compat
from .saver import Saver


class DirectoryExistsError(Exception):
    """Attempt to overwrite directory that doesn't contain freezeyt output"""


class FileSaver(Saver):
    """Outputs frozen pages as files on the filesystem.

    base - Filesystem base path (eg. /tmp/)
    prefix - Base URL to deploy web app in production
        (eg. url_parse('http://example.com:8000/foo/')
    """
    def __init__(self, base_path, prefix):
        self.base_path = base_path.resolve()
        self.prefix = prefix

    async def prepare(self):
        if self.base_path.exists():
            has_files = list(self.base_path.iterdir())
            has_index = self.base_path.joinpath('index.html').exists()
            if has_files and not has_index:
                raise DirectoryExistsError(
                    f'Will not overwrite directory {self.base_path}: it '
                    + 'contains files that do not look like a frozen website. '
                    + 'If you are sure, remove the directory before running '
                    + 'freezeyt.'
                )
            shutil.rmtree(self.base_path)

    async def save_to_filename(self, filename, content_iterable):
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        loop = compat.get_running_loop()

        absolute_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(absolute_filename, "wb") as f:
            for item in content_iterable:
                await loop.run_in_executor(None, f.write, item)

    async def open_filename(self, filename):
        absolute_filename = self.base_path / filename
        assert self.base_path in absolute_filename.parents

        return open(absolute_filename, 'rb')

    async def finish(self, success: bool, cleanup: bool, gh_pages: bool):
        """Delete incomplete directory after a failed freeze or
        add files from output directory to git gh-pages branch (and create it)
        after a successful freeze.
        """
        if not success and cleanup and self.base_path.exists():
            shutil.rmtree(self.base_path)
        elif success and gh_pages and self.base_path.exists():
            with open(str(self.base_path / "CNAME"), 'w') as f:
                f.write(self.prefix.host)
            with open(str(self.base_path / ".nojekyll"), 'w'): 
                pass # only create the empty file
            try:
                sp_params = {"stderr": STDOUT, "shell": True, "cwd": self.base_path}
                check_output("git init -b gh-pages", **sp_params)
                check_output("git add .", **sp_params)
                check_output('git commit -m "added all freezed files"', **sp_params)
            except CalledProcessError as e:
                print(dedent(f"""
                      Freezing was successful, but a problem occurs during the execution of one of commands for creating git gh-pages branch:
                      command: {e.cmd}
                      captured standard output with error:
                      {e.stdout.decode()}"""))
