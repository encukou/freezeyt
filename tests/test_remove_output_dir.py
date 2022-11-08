import pytest
import os
import shutil

from freezeyt import freeze, DirectoryExistsError
from freezeyt.filesaver import FileSaver

from fixtures.app_with_extra_files.app import app, freeze_config


def test_do_not_overwrite_existing_dir(tmp_path):
    builddir = tmp_path / 'build'
    builddir.mkdir()
    file_path = builddir / 'important.dat'
    file_path.write_text('1234')

    config = {
        **freeze_config,
        'output': {'type': 'dir', 'dir': builddir},
    }

    with pytest.raises(DirectoryExistsError):
        freeze(app, config)


def test_overwrite_empty_dir(tmp_path):
    builddir = tmp_path / 'build'
    builddir.mkdir()
    index_path = builddir / 'index.html'

    config = {
        **freeze_config,
        'output': {'type': 'dir', 'dir': builddir},
    }

    freeze(app, config)
    assert index_path.exists()


def test_overwrite_dir_with_index(tmp_path):
    builddir = tmp_path / 'build'
    builddir.mkdir()
    index_path = builddir / 'index.html'
    index_path.write_text('<html></html>')

    old_path = builddir / 'old.dat'
    old_path.write_text('1234')

    old_dir_path = builddir / 'dir'
    old_dir_path.mkdir()

    config = {
        **freeze_config,
        'output': {'type': 'dir', 'dir': builddir},
    }

    freeze(app, config)
    assert index_path.exists()

    assert not old_path.exists()
    assert not old_dir_path.exists()


def test_rm_output_dir_with_protected_file(tmp_path):
    """We test that if there is an index.html in the directory and a file with permissions 000
    (protected file) is in dir too, the directory will be overwritten successfully."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    protected_file = output_dir / "protected.file"
    protected_file.touch()
    protected_file.chmod(0o000)
    index_path = output_dir / 'index.html'
    index_path.write_text('<html></html>')
    config = {
        **freeze_config,
        'output': {'type': 'dir', 'dir': output_dir},
    }
    freeze(app, config)
    assert not protected_file.exists()

if os.name == "nt": # this test will run only on Windows systems
    def test_add_write_flag_on_windows(tmp_path):
        """We are testing that we need to use the add_write_flag method (as an onerror
        parameter to the rmtree method) on Windows, otherwise rmtree on Windows will not be
        able to delete protected files in output dir - for example, some files in the .git
        directory."""
        protected_file = tmp_path / "protected.file"
        protected_file.touch()
        protected_file.chmod(0o000)
        with pytest.raises(PermissionError): # without onerror=add_write_flag
            shutil.rmtree(tmp_path)
        assert protected_file.exists()
        shutil.rmtree(tmp_path, onerror=FileSaver.add_write_flag)
        assert not tmp_path.exists()
        assert not protected_file.exists()
