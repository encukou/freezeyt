from freezeyt import freeze
from freezeyt.freezer import VersionMismatch
from freezeyt import __version__

from fixtures.app_with_extra_files.app import app
import pytest

v = (__version__).split(".")[0]
good_config_version = [
     v, int(v), f"{v}.x", f"{v}.xx", f"{v}.1", f"{v}.11",
]

bad_config_version = [
    "", "-", 0, f" {v}.1", -int(v)+1, int(v.split(".")[0])+1, int(v)-1, int(v)-100, "x", "xx", "x.1", "x.10", 1.1
]

@pytest.mark.parametrize('version', good_config_version)
def test_version_config_is_ok(version):
    config = {"version": version, "output": {"type": "dict"}}
    freeze(app, config)

@pytest.mark.parametrize('version', bad_config_version)
def test_version_config_is_bad(version):
    config = {"version": version, "output": {"type": "dict"}}
    with pytest.raises(VersionMismatch):
        freeze(app, config)
