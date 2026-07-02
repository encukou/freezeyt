from freezeyt import freeze
from freezeyt.freezer import VersionMismatch
from freezeyt import __version__, _min_config_version

from testutil import context_for_test
import pytest

v = (__version__).split(".")[0]
_min = int(_min_config_version)
good_config_versions = [
    # current versions
    v, int(v), f"{v}.x", f"{v}.xx", f"{v}.1", f"{v}.11", f" {v}.1",

    # older versions
    _min, 1, "1", "1.1", " 1 ",

    # no check
    None,
]

bad_config_versions = [
    "", "-", 0, -int(v)+1, int(v.split(".")[0])+1, _min-1, int(v)-100,
    "x", "xx", "x.1", "x.10", 1.1
]

@pytest.mark.parametrize('version', good_config_versions)
def test_version_config_is_ok(version):
    with context_for_test('app_with_extra_files') as module:
        config = {"version": version, "output": {"type": "dict"}}
        freeze(module.app, config)

@pytest.mark.parametrize('version', bad_config_versions)
def test_version_config_is_bad(version):
    with context_for_test('app_with_extra_files') as module:
        config = {"version": version, "output": {"type": "dict"}}
        with pytest.raises(VersionMismatch):
            freeze(module.app, config)
