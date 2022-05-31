from freezeyt.mimetype_check import get_mimetype_checker


class Middleware:
    def __init__(self, app, config):
        self.app = app

        self.check_mimetype = get_mimetype_checker(config)

    def __call__(self, environ, start_response):
        headers = None

        def middleware_start_response(status, response_headers, exc_info=None):
            nonlocal headers
            headers = response_headers
            return start_response(status, response_headers, exc_info)

        result = self.app(environ, middleware_start_response)
        if headers is None:
            raise Exception('WSGI application did not call start_response')

        self.check_mimetype(environ['PATH_INFO'], headers)
        return result
