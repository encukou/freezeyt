import pytest

from flask import Flask

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


def test_warn_freezing_index_from_diff_routes(capsys):
    """Test if we get warning when app defines '/' and 'index.html'
    as diferent routes, probably with different content.
    """

    app = Flask(__name__)

    index_routes = ['/', '/index.html']
    second_page_routes = ['/second_page/', '/second_page/index.html']

    @app.route(index_routes[0])
    def index():
        return """
    <a href='/index.html'>INDEX FILE</a>
    <a href='/second_page/index.html'>SECOND PAGE FILE</a>
"""

    @app.route(index_routes[1])
    def index_html():
        return "INDEX FILE"

    @app.route(second_page_routes[0])
    def second_page():
        return "SECOND PAGE"

    @app.route(second_page_routes[1])
    def second_page_html():
    # Link to index.html test if warning is
    # printing out only once
        return """
    <a href='/second_page/'>SECOND PAGE</a>
    <a href='/index.html'>INDEX FILE</a>
"""

    config = {
        'prefix': 'http://example.test/',
        'output': {'type': 'dict'},
    }

    freeze(app, config)

    captured = capsys.readouterr()
    stdout = captured.out

    warnings_counter = 0
    print(f"{stdout=}")
    for l in stdout.splitlines():
        print(f"{l=}")
        if l.startswith("[WARNING]"):
            warnings_counter += 1

    assert warnings_counter == 2

    index_warn = f"[WARNING] One static file is requested from different paths {index_routes}"
    second_page_warn = f"[WARNING] One static file is requested from different paths {second_page_routes}"

    assert index_warn in stdout
    assert second_page_warn in stdout

