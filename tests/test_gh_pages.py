from freezeyt import freeze

from fixtures.app_2pages.app import app
import pytest

def test_gh_pages_files_were_created(tmp_path):
    """Test if CNAME and .nojekyll files were created."""
    output_dir = tmp_path / "output"
    config = {"output": str(output_dir)}
    config.setdefault(
            'plugins', []).append('freezeyt.plugins:GHPagesPlugin')
    freeze(app, config)
    assert (output_dir / "CNAME").exists() # the CNAME file has to exist
    assert (output_dir / ".nojekyll").exists() # the .nojekyll has to exist
    

def test_cname_has_prefix(tmp_path):
    """Test if CNAME has prefix text writen inside."""
    output_dir = tmp_path / "output"
    config = {"prefix": "https://jiri.one/", "output": str(output_dir)}
    config.setdefault(
            'plugins', []).append('freezeyt.plugins:GHPagesPlugin')
    freeze(app, config)
    assert (output_dir / "CNAME").exists() # the CNAME file has to exist
    with open(output_dir / "CNAME", "r") as f:
            assert "jiri.one" == f.read()

def test_git_gh_pages_branch_is_ok(tmp_path):
    """Test if gh-pages branch created and all files are added to it correctly."""
    output_dir = tmp_path / "output"
    config = {"prefix": "https://jiri.one/", "output": str(output_dir)}
    config.setdefault(
            'plugins', []).append('freezeyt.plugins:GHPagesPlugin')
    freeze(app, config)
    assert (output_dir / ".git").exists() # the .git directory has to exist
    assert (output_dir / ".git").is_dir() # the .git directory has to be directory
    assert (output_dir / ".git/refs/heads/gh-pages").exists() # the gh-pages has to be git head branch
    with open(output_dir / ".git/HEAD", "r") as f:
        assert "gh-pages" in f.read().strip().split("/") # the gh-pages has to be git head branch
    with open(output_dir / ".git/COMMIT_EDITMSG", "r") as f:
        assert "\"added all freezed files\"" in f.read().strip() # last commit with all files
