import pytest

from freezeyt import freeze

from testutil import context_for_test


PREFIX_MULTI_SLASH = (
    "https://example.test/a//",
    "https://example.test////a/",
)
@pytest.mark.parametrize('prefix', PREFIX_MULTI_SLASH)
def test_warn_multi_slashes_prefix(capsys, prefix):
    config = {
        'prefix': prefix,
        'output': {'type': 'dict'},
    }

    with context_for_test('app_simple') as module:
        freeze(module.app, config)
        captured = capsys.readouterr()

    expected_output = (
        "[WARNING] Freezeyt reduces multiple consecutive"
        f" slashes in {prefix!r} to one\n"
    )

    assert expected_output in captured.out
