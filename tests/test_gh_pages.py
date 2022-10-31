from subprocess import check_output
import pytest
# internal imports
from freezeyt import freeze
from fixtures.app_2pages.app import app


def test_gh_pages_files_were_created(tmp_path):
    """Test if CNAME and .nojekyll files were created."""
    output_dir = tmp_path / "output"
    config = {"gh_pages": True, "output": str(output_dir)}
    freeze(app, config)
    assert (output_dir / "CNAME").exists() # the CNAME file has to exist
    assert (output_dir / ".nojekyll").exists() # the .nojekyll has to exist
    

def test_cname_has_prefix(tmp_path):
    """Test if CNAME has prefix text writen inside."""
    output_dir = tmp_path / "output"
    config = {"gh_pages": True,
              "prefix": "https://jiri.one/",
              "output": str(output_dir)}
    freeze(app, config)
    assert "jiri.one" == (output_dir / "CNAME").read_text()

def test_git_gh_pages_branch_is_ok(tmp_path):
    """Test if gh-pages branch created and all files are added to it correctly."""
    output_dir = tmp_path / "output"
    config = {"gh_pages": True,
              "prefix": "https://jiri.one/",
              "output": str(output_dir)}
    freeze(app, config)
    head_name = check_output(["git", "name-rev", "--name-only", "HEAD"], cwd=output_dir).decode().strip() # get name of HEAD branch
    assert "gh-pages" == head_name # the gh-pages has to be git head branch
    last_commit_info = check_output(["git", "rev-list", "--oneline", "HEAD"], cwd=output_dir).decode().strip()
    last_commit_hash, last_commit_text = last_commit_info.split(" ", 1)
    assert "added all freezed files" == last_commit_text # text of last commit with all files
    # get list of all committed files
    commited_files = check_output(["git", "ls-tree", "--name-only", "-r", last_commit_hash], cwd=output_dir).decode().strip().split()
    # list of expected files, which has to be same like commited_files
    expected_files = ['.nojekyll', 'CNAME', 'index.html', 'second_page.html']
    for file_committed, file_expected in zip(commited_files, expected_files):
        assert file_committed == file_expected

def test_gh_pages_is_disabled(tmp_path):
    """Test with disabled gh_pages config (set to False)."""
    output_dir = tmp_path / "output"
    config = {"gh_pages": False, "output": str(output_dir)}
    freeze(app, config)
    assert not (output_dir / ".git").exists() # the .git directory has not to exist
    assert not (output_dir / "CNAME").exists() # the CNAME file has not to exist
    assert not (output_dir / ".nojekyll").exists() # the .nojekyll has not to exist

def test_gh_pages_is_disabled_by_default(tmp_path):
    """Test that gh_pages config is completely ommited, so disabled by default."""
    output_dir = tmp_path / "output"
    config = {"output": str(output_dir)}
    freeze(app, config)
    assert not (output_dir / ".git").exists() # the .git directory has not to exist
    assert not (output_dir / "CNAME").exists() # the CNAME file has not to exist
    assert not (output_dir / ".nojekyll").exists() # the .nojekyll has not to exist


def test_gh_pages_raise_exception_if_path_in_prefix(tmp_path):
    """Test that if the user specifies path in the prefix while using the gh-pages plugin, an exception will be thrown."""
    output_dir = tmp_path / "output"
    config = {"gh_pages": True,
              "prefix": "https://jiri.one/SOME_PATH/",
              "output": str(output_dir)}
    with pytest.raises(ValueError, match="When using the Github Pages plugin, you can't specify a path in the prefix, so github can't handle it."):
        freeze(app, config)


def test_gh_pages_two_times_in_same_folder(tmp_path):
    """Test in which we run freezeyt twice with the same output directory - we do not expect an exception and the directory at the end must contain only the correct files."""
    output_dir = tmp_path / "output"
    config = {"gh_pages": True,
              "output": str(output_dir)}
    freeze(app, config)
    freeze(app, config)
    expected_files = {'.nojekyll', 'CNAME', 'index.html', 'second_page.html'}
    # the .git directory is not created on all systems/configurations
    got_files = {path.name for path in output_dir.iterdir() if path.name != ".git"}
    assert got_files == expected_files
