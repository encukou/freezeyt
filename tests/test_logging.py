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


def test_warn_same_frozen_file_from_different_URLs(capsys):
    """App can define different URLs with different content,
    which are saved then as one static file by Freezeyt
    (e.g. '/' and '/index.html'). One content will be always lost.
    If this situation occurs, we should get a warning at least.
    """

    app = Flask(__name__)

    index_routes = ['', 'index.html', 'index.html?a=b']
    second_page_routes = ['second_page/', 'second_page/index.html']

    @app.route('/' + index_routes[0])
    def index():
        return """
    <a href='/index.html'>INDEX FILE</a>
    <a href='/index.html?a=b'>INDEX FILE</a>
    <a href='http://example.test'>INDEX ABSOLUTE URL</a>
    <a href='http://example.test/'>INDEX ABSOLUTE URL WITH SLASH</a>
    <a href='/second_page/index.html'>SECOND PAGE FILE</a>
    <a href='/second_page/index.html#frag'>SECOND PAGE WITH FRAGMENT</a>
"""

    @app.route('/' + index_routes[1])
    def index_html():
        return "INDEX FILE"

    @app.route('/' + second_page_routes[0])
    def second_page():
        return "SECOND PAGE"

    @app.route('/' + second_page_routes[1])
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
    for l in stdout.splitlines():
        if l.startswith("[WARNING]"):
            warnings_counter += 1

    assert warnings_counter == 2

    index_warn = (
        "[WARNING] Static file 'index.html' is requested"
        f" from different URLs {index_routes}"
    )
    second_page_warn = (
        "[WARNING] Static file 'second_page/index.html' is requested"
        f" from different URLs {second_page_routes}"
    )

    assert index_warn in stdout
    assert second_page_warn in stdout



def test_no_warn_index_slash(capsys):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return """
            <a href='http://example.test'>INDEX ABSOLUTE URL</a>
            <a href='http://example.test/'>INDEX ABSOLUTE URL WITH SLASH</a>
        """

    config = {
        'prefix': 'http://example.test/',
        'output': {'type': 'dict'},
    }

    freeze(app, config)

    captured = capsys.readouterr()
    assert 'WARNING' not in captured.out
