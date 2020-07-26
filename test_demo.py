import pytest

from demo_app import app
from demo_app_2pages import app as app_2pages
from demo_app_3pages_deep import app as app_3pages_deep
from demo_app_2pages_cycle import app as app_2pages_cycle

from freezeyt import freeze


def test_one_page(tmp_path):
    """
    Tests if the freezer creates a file from a one-page app.
    """
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
    """
    Tests if the freezer creates files from a two-page app
    where the first page links to the second page.
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
    """
    Tests if the freezer creates files from a web app
    where the first page links to the second page
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
    """
    Tests if the freezer creates two pages
    and doesn't get into an infinite loop.
    """
    freeze(app_2pages_cycle, tmp_path)

    path1 = tmp_path / "index.html"
    assert path1.exists()
    assert 'Hello world!' in path1.read_text()

    path2 = tmp_path / "second_page.html"
    assert path2.exists()
    assert 'Hello world second page' in path2.read_text()
