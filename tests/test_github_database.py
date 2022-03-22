from unittest.mock import patch
from testutil import context_for_test
from freezeyt import freeze

MIMETYPE_DB = {
    'html': 'mocked_html_mimetype/html'
}


@patch(
    'freezeyt.freezer.parse_mimetype_db',
    return_value=MIMETYPE_DB,
)
def test_github_mimetypes(tmp_path):
    """Test
    """
    builddir = tmp_path / 'build'

    with context_for_test('app_simple') as module:
        freeze_config = {
            'output': str(builddir),
            'mimetype_db': 'path/to/db.json'
        }

        freeze(module.app, freeze_config)