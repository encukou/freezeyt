class ASGIMiddleware:
    def __init__(self, app, config):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
