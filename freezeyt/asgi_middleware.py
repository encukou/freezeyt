from freezeyt.wsgi_middleware import WSGIMiddleware
from freezeyt.wsgi_to_asgi import WSGIToASGIMiddleware
from freezeyt.urls import PrefixURL

class ASGIMiddleware:
    def __init__(self, app, config, *, prefix=None):

        app_interface = config.get('app_interface', 'wsgi')
        if app_interface == 'wsgi':
            app = WSGIMiddleware(app, config)
            if prefix is None:
                prefix = PrefixURL.from_config(config)
            app = WSGIToASGIMiddleware(app, prefix=prefix)
        elif app_interface == 'asgi':
            pass
        else:
            raise ValueError(
                'app_interface must be "asgi" or "wsgi", '
                + f'got {app_interface!r}'
            )

        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
