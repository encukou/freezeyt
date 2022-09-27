from freezeyt.mimetype_check import MimetypeChecker


class Middleware:
    def __init__(self, app, config):
        self.app = app
        self.mimetype_checker = MimetypeChecker(config)

    def __call__(self, environ, server_start_response):

        path_info = environ.get('PATH_INFO', '')

        def mw_start_response(status, headers, exc_info=None):
            result = server_start_response(status, headers, exc_info)
            self.mimetype_checker.check(path_info, headers)
            return result

        return self.app(environ, mw_start_response)
