
class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, server_start_response):

        def mw_start_response(status, headers, exc_info=None):
            result = server_start_response(status, headers, exc_info)
            return result

        return self.app(environ, mw_start_response)
