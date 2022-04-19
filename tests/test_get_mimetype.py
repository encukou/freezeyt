import pytest
from pathlib import Path
from freezeyt import freeze
from testutil import context_for_test


def my_get_mimetype(url_path):
    suffix = Path(url_path).suffix

    if suffix == '.html':
        return ["text/html"]
    return ["text/plain"]

GET_MIMETYPES = {
    'python_get_mimetype': my_get_mimetype,
    'string_get_mimetype': 'test_get_mimetype:my_get_mimetype',
}


@pytest.mark.parametrize('get_mimetypeID', GET_MIMETYPES)
def test_succesfully_loaded_get_mimetype_config(tmp_path, get_mimetypeID):
    """Test if user configuration of external functions get_mimetype
    is loaded and used during web app freezing.
    """
    builddir = tmp_path / 'build'

    with context_for_test('default_mimetype_plain') as module:
        freeze_config = {
            'output': str(builddir),
            'get_mimetype': GET_MIMETYPES[get_mimetypeID],
        }

        freeze(module.app, freeze_config)

        assert (builddir / 'index.html').exists()
        assert (builddir / 'textfile').exists()
