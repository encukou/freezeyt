from subprocess import check_output

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
    assert (output_dir / "CNAME").exists() # the CNAME file has to exist
    with open(output_dir / "CNAME", "r") as f:
        assert "jiri.one" == f.read()

def test_git_gh_pages_branch_is_ok(tmp_path):
    """Test if gh-pages branch created and all files are added to it correctly."""
    output_dir = tmp_path / "output"
    config = {"gh_pages": True,
              "prefix": "https://jiri.one/",
              "output": str(output_dir)}
    freeze(app, config)
    assert (output_dir / ".git").exists() # the .git directory has to exist
    assert (output_dir / ".git").is_dir() # the .git directory has to be directory
    assert (output_dir / ".git/refs/heads/gh-pages").exists() # the gh-pages has to be git head branch
    with open(output_dir / ".git/HEAD", "r") as f:
        assert "gh-pages" in f.read().strip().split("/") # the gh-pages has to be git head branch
    with open(output_dir / ".git/COMMIT_EDITMSG", "r") as f:
        assert "\"added all freezed files\"" == f.read().strip() # text of last commit with all files
    with open(output_dir / ".git/refs/heads/gh-pages", "r") as f:
        commit_hash = f.read().strip() # get last commit hash
    # get list of all committed files
    commited_files = check_output(["git", "show", "--pretty=", "--name-only", commit_hash], cwd=output_dir).decode().strip().split()
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

# ONLY FOR DISCUSSION
# def test_gh_pages_with_dict_output():
#     """Test that gh_pages config is enabled together with dict output"""
#     config = {'output': {'type': 'dict'},
#               "gh_pages": True}
#     freeze(app, config)
