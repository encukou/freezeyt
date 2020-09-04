import pytest

from demo_app_url_for import app as app_url_for

from freezeyt import freeze


def test_flask_url_for_custom_prefix_with_port(tmp_path):
    """Test an app unsing Flask url_for() with custom host & path
    """

    freeze(app_url_for, tmp_path, prefix='http://freezeyt.test:1234/foo/')

    with open(tmp_path / "index.html", encoding='utf-8') as f:
        read_text = f.read()

    assert 'http://freezeyt.test:1234/foo/second_page.html' in read_text
    assert '/foo/third_page.html' in read_text

    path2 = tmp_path / "second_page.html"
    assert path2.exists()

    path3 = tmp_path / "third_page.html"
    assert path3.exists()


def test_flask_url_for_custom_prefix_without_port(tmp_path):
    """Test an app unsing Flask url_for() with custom host & path
    """

    freeze(app_url_for, tmp_path, prefix='http://freezeyt.test/foo/')

    with open(tmp_path / "index.html", encoding='utf-8') as f:
        read_text = f.read()

    assert 'http://freezeyt.test/foo/second_page.html' in read_text
    assert '/foo/third_page.html' in read_text

    path2 = tmp_path / "second_page.html"
    assert path2.exists()

    path3 = tmp_path / "third_page.html"
    assert path3.exists()
