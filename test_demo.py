import pytest
from demo_app import app

from freezeyt import freeze


def test_one_page(tmp_path):
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
            <br>
            <a href='/second_page'>LINK</a> to second page.
        </body>
    </html>
    """


def test_two_pages(tmp_path):
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
            <br>
            <a href='/second_page'>LINK</a> to second page.
        </body>
    </html>
    """

    with open(tmp_path / "second_page.html", encoding='utf-8') as f2:
        read_text2 = f2.read()

    assert read_text2 == """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Second page !!!
        </body>
    </html>
    """
