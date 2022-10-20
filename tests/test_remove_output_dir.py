import pytest
import os
import shutil

from freezeyt import freeze, DirectoryExistsError

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
    """We test that if there is an index.html in the directory and a file with permissions 000 (protected file), the directory will be overwritten successfully."""
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


def test_rm_output_dir_with_protected_file_on_windows_fail(tmp_path, monkeypatch):
    """We test that if there is an index.html file in the directory and a file with permissions 000 (protected file) is in dir too, then if we use rmtree without the onerror parameter, which otherwise calls the internal add_write_flag method, an exception is raised on Windows systems (os.name == 'nt'). On other systems, the deletion should be successful without the internal add_write_flag method too."""
    from shutil import rmtree as rmtree_for_mocking
    def mock_rmtree(path, onerror=None):
        """Mocked rmtree method, which only get rid of the onerror parameter."""
        return rmtree_for_mocking(path)
    monkeypatch.setattr(shutil, "rmtree", mock_rmtree)
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
    if os.name == "nt":
        with pytest.raises(PermissionError):
            freeze(app, config)
        assert protected_file.exists()
    else:
        freeze(app, config)
        assert not protected_file.exists()
