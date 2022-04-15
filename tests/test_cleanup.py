from freezeyt import freeze, DirectoryExistsError, UnexpectedStatus
from testutil import raises_multierror_with_one_exception
from fixtures.app_cleanup_config.app import app
import pytest


def test_let_incomplete_dir_intact(tmp_path):
    output_dir = tmp_path / "output"
    config = {"cleanup": False, "output": str(output_dir)}
    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(app, config)
    assert output_dir.exists() == True # the output dir has to exist
    assert (output_dir / "index.html").exists() == True # the index.html file inside output dir has to exist


def test_remove_incomplete_dir(tmp_path):
    output_dir = tmp_path / "output2"
    config = {"cleanup": True, "output": str(output_dir)}
    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(app, config)
    assert output_dir.exists() == False # the output dir has to be gone


def test_remove_incomplete_dir_by_default(tmp_path):
    output_dir = tmp_path / "output3"
    config = {"output": str(output_dir)}
    with raises_multierror_with_one_exception(UnexpectedStatus):
        freeze(app, config)
    assert output_dir.exists() == False # the output dir has to be gone


def test_do_not_cleanup_if_directory_exists_error(tmp_path):
    output_dir = tmp_path / "output4"
    output_dir.mkdir()
    file_path = output_dir / 'important.dat'
    file_path.write_text('inportant text')

    config = {"cleanup": True, "output": str(output_dir)}

    with pytest.raises(DirectoryExistsError):
        freeze(app, config)

    assert output_dir.exists() == True # the output dir has to exist
    assert (output_dir / 'important.dat').exists() == True # the important.dat file inside output dir has to exist

