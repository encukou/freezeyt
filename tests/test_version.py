from freezeyt import freeze
from freezeyt.freezer import VersionMismatch, VERSION as v

from fixtures.app_with_extra_files.app import app
import pytest


good_config_version = [
    v, int(v), f" {v}.1", f"{v}.x", f"{v}.xx", f"{v}.1", f"{v}.11", float(f"{v}.1"), float(f"{v}.11"),
]

bad_config_version = [
    "", "-", 0, -int(v)+1, int(v)+1, int(v)-1, int(v)-100, "x", "xx", "x.1", "x.10", float(f"-{v}.1"), float(f"-{v}.11")
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
