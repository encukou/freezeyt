import pytest
from demo_app import app

from freezeyt import freeze


def test_one_page(tmp_path):
    freeze(app, tmp_path)

    with open(tmp_path / "index.html", encoding="utf-8") as f:
        read_text = f.read()

    assert (
        read_text
        == """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!<br>
            <a href="/about">About page</a>
        </body>
    </html>
    """
    )


def test_two_pages(tmp_path):
    freeze(app, tmp_path)

    with open(tmp_path / "index.html", encoding="utf-8") as f:
        first_page = f.read()
    with open(tmp_path / "about.html", encoding="utf-8") as f:
        second_page = f.read()

    assert (
        first_page
        == """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!<br>
            <a href="/about">About page</a>
        </body>
    </html>
    """
    )
    assert (
        second_page
        == """
    <html>
        <head>
            <title>About</title>
        </head>
        <body>
            <h2>We are czech community of PyLadies !!!</h2>
        </body>
    </html>
    """
    )

