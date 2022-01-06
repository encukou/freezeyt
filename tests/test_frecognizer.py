import pytest
from pathlib import Path
from freezeyt import freeze
from testutil import context_for_test


def my_recognizer(url_path):
    suffix = Path(url_path).suffix

    if suffix == '.html':
        return ("text/html", None)
    return ("text/plain", None)

FRECOGNIZERS = {
    'python_recognizer': my_recognizer,
    'string_recognizer': 'test_frecognizer:my_recognizer',
}


@pytest.mark.parametrize('frecognizerID', FRECOGNIZERS)
def test_succesfully_loaded_frecognizer_config(tmp_path, frecognizerID):
    """Test
    """
    builddir = tmp_path / 'build'

    with context_for_test('default_mimetype_plain') as module:
        freeze_config = {
            'output': str(builddir),
            'filetype_recognizer': FRECOGNIZERS[frecognizerID],
        }

        freeze(module.app, freeze_config)

        assert (builddir / 'index.html').exists()
        assert (builddir / 'textfile').exists()
