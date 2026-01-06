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

        self.static_mode = config.get('static_mode', False)

    async def __call__(self, scope, receive, send):
        if scope['method'] != 'GET':
            # The Freezer only sends GET requests.
            # When we get another method, we know it came from another WSGI
            # server. Handle it specially.
            await self.handle_non_get(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def handle_non_get(self, scope, receive, send):
        # Handle requests other than GET. These can't come from Freezeyt.
        if not self.static_mode:
            # Normally, pass all other requests to the app unchanged.
            await self.app(scope, receive, send)
            return

        # In static mode, disallow everything but GET, HEAD, OPTIONS.

        if scope['method'] == 'HEAD':
            # For HEAD, call the app but ignore the response body
            new_scope = {**scope, 'method': 'GET'}
            async def filtered_send(event):
                if event['type'] == "http.response.start":
                    await send(event)
                    await send({'type': "http.response.body"})
            await self.app(scope, receive, filtered_send)
            return
        elif scope['method'] == 'OPTIONS':
            # For OPTIONS, give our own response
            # (The status should be '204 No Content', but according to
            # MDN, some browsers misinterpret that, so '200' is safer.)
            while True:
                event = await receive()
                if event['type'] == "http.request":
                    await send({
                        "type": "http.response.start",
                        "status": 200,  # OK
                        "headers": [(b'Allow', b'GET, HEAD, OPTIONS')],
                    })
                    await send({
                        "type": "http.response.body",
                    })
                    break
            return
        else:
            # Disallow other methods
            while True:
                event = await receive()
                if event['type'] == "http.request":
                    await send({
                        "type": "http.response.start",
                        "status": 405,  # Method not allowed
                    })
                    await send({
                        "type": "http.response.body",
                    })
                    break
            return
