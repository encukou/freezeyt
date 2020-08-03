import pytest

from demo_app import app
from demo_app_2pages import app as app_2pages
from demo_app_3pages_deep import app as app_3pages_deep
from demo_app_2pages_cycle import app as app_2pages_cycle
from demo_app_external_link import app as app_external_link
from demo_app_url_for import app as app_url_for

from freezeyt import freeze


def test_one_page(tmp_path):
    """Test if the freezer creates a file from a one-page app."""
    freeze(app, tmp_path)

    with open(tmp_path / "index.html", encoding='utf-8') as f:
        read_text = f.read()

    assert read_text == """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """


def test_two_pages(tmp_path):
    """Test if the freezer creates files from a two-page app.

    In the app the first (index) page links to the second page.
    """
    freeze(app_2pages, tmp_path)

    with open(tmp_path / "index.html", encoding='utf-8') as f:
        read_text = f.read()

    assert read_text == """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href='/second_page.html'>LINK</a> to second page.
        </body>
    </html>
    """

    with open(tmp_path / "second_page.html", encoding='utf-8') as f2:
        read_text2 = f2.read()

    assert read_text2 == """
    <html>
        <head>
            <title>Hello world second page</title>
        </head>
        <body>
            Second page !!!
        </body>
    </html>
    """


def test_three_pages_deep(tmp_path):
    """Test if the freezer creates files from a 3-page web app.

    In the app the first page links to the second page
    and the second page links to the third page.
    """
    freeze(app_3pages_deep, tmp_path)

    path1 = tmp_path / "index.html"
    assert path1.exists()

    path2 = tmp_path / "second_page.html"
    assert path2.exists()

    path3 = tmp_path / "third_page.html"
    assert path3.exists()
    assert 'Hello world third page' in path3.read_text()


def test_two_pages_cycle(tmp_path):
    """Test if the freezer creates two pages from a web app.

    Test if the freezer doesn't get into an infinite loop. In the app
    the index/home page links to the second page and also to itself.
    """
    freeze(app_2pages_cycle, tmp_path)

    path1 = tmp_path / "index.html"
    assert path1.exists()
    assert 'Hello world!' in path1.read_text()

    path2 = tmp_path / "second_page.html"
    assert path2.exists()
    assert 'Hello world second page' in path2.read_text()


def test_external_link(tmp_path):
    """Test if the freezer ignores external links.
    """

    freeze(app_external_link, tmp_path)

    path1 = tmp_path / "index.html"
    assert path1.exists()
    assert 'Hello world!' in path1.read_text()

    tmpdir_contents = list(tmp_path.iterdir())
    assert tmpdir_contents == [path1]


def test_flask_url_for(tmp_path):
    """Test if flask func url_for() run correctly.
    """

    freeze(app_url_for, tmp_path)

    with open(tmp_path / "index.html", encoding='utf-8') as f:
        read_text = f.read()

    assert 'http://localhost:8000/second_page.html' in read_text
    assert '/third_page.html' in read_text

    path2 = tmp_path / "second_page.html"
    assert path2.exists()

    path3 = tmp_path / "third_page.html"
    assert path3.exists()
