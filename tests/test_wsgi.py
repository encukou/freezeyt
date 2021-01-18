"""Test handling of details of the WSGI protocol"""

import sys

import pytest

from freezeyt import freeze


class InternalServerError(Exception):
    """Simulated 500 error"""


def test_exc_info():
    def simple_app(environ, start_response):
        try:
            # regular application code here
            status = "200 OK"
            response_headers = [("content-type", "text/html")]
            start_response(status, response_headers)
            raise InternalServerError('something went wrong')
            return ["normal body goes here"]
        except Exception:
            status = "500 Internal Server Error"
            response_headers = [("content-type", "text/html")]
            start_response(status, response_headers, sys.exc_info())
            return [b"error body goes here"]

    config = {'output': 'dict'}

    with pytest.raises(InternalServerError):
        freeze(simple_app, config)


def test_exc_info_none():
    def simple_app(environ, start_response):
        # regular application code here
        status = "200 OK"
        response_headers = [("content-type", "text/html")]
        start_response(status, response_headers, (None, None, None))
        return [b"normal body goes here"]

    config = {'output': 'dict'}
    expected = {'index.html': b'normal body goes here'}

    assert freeze(simple_app, config) == expected


def test_write():
    def simple_app(environ, start_response):
        # regular application code here
        status = "200 OK"
        response_headers = [("content-type", "text/html")]
        write = start_response(status, response_headers)
        write(b'here ')
        write(b'is the ')
        return [b'response ', b'body']

    config = {'output': 'dict'}
    expected = {'index.html': b'here is the response body'}

    assert freeze(simple_app, config) == expected
