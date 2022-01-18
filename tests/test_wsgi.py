"""Test handling of details of the WSGI protocol"""

import sys

import pytest

from freezeyt import freeze

from testutil import raises_multierror_with_one_exception


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

    config = {'output': {'type': 'dict'}}

    with raises_multierror_with_one_exception(InternalServerError):
        freeze(simple_app, config)


def test_exc_info_none():
    def simple_app(environ, start_response):
        # regular application code here
        status = "200 OK"
        response_headers = [("content-type", "text/html")]
        start_response(status, response_headers, (None, None, None))
        return [b"normal body goes here"]

    config = {'output': {'type': 'dict'}}
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

    config = {'output': {'type': 'dict'}}
    expected = {'index.html': b'here is the response body'}

    assert freeze(simple_app, config) == expected


@pytest.mark.parametrize('iterable', (
    (b'a', b'b'),
    [b'a', b'b'],
    {b'a': 1, b'b': 2},
    (value for value in (b'a', b'b')),
))
def test_result_iterable_types(iterable):
    def simple_app(environ, start_response):
        # regular application code here
        status = "200 OK"
        response_headers = [("content-type", "text/html")]
        start_response(status, response_headers)
        return iterable

    config = {'output': {'type': 'dict'}}
    expected = {'index.html': b'ab'}

    assert freeze(simple_app, config) == expected


def test_close():
    closed = False

    class SpecialResult:
        def __init__(self):
            self.values = [b'body', b' ', b'content']
            self.position = 0

        def __next__(self):
            if self.position < len(self.values):
                value = self.values[self.position]
                self.position += 1
                return value
            else:
                raise StopIteration()

        def __iter__(self):
            return self

        def close(self):
            nonlocal closed
            closed = True

    def simple_app(environ, start_response):
        # regular application code here
        status = "200 OK"
        response_headers = [("content-type", "text/html")]
        start_response(status, response_headers)
        return SpecialResult()

    config = {'output': {'type': 'dict'}}
    expected = {'index.html': b'body content'}

    assert freeze(simple_app, config) == expected
    assert closed == True
