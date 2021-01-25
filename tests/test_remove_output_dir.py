import pytest

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

    config = {
        **freeze_config,
        'output': {'type': 'dir', 'dir': builddir},
    }

    freeze(app, config)
    assert index_path.exists()
