from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.exceptions import NotFound, Forbidden
from werkzeug.security import safe_join

from freezeyt.wsgi_to_asgi import WSGIToASGIMiddleware
from freezeyt.urls import PrefixURL
from freezeyt.extra_files import get_extra_files
from freezeyt.mimetype_check import MimetypeChecker

FILE_CHUNK_SIZE = 1024*4

class ASGIMiddleware:
    def __init__(self, app, config, *, prefix=None):

        app_interface = config.get('app_interface', 'wsgi')
        if app_interface == 'wsgi':
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
        self.prefix = prefix
        self.mimetype_checker = MimetypeChecker(config)

        self.url_map = Map()
        for url_part, kind, content_or_path in get_extra_files(config):
            if '<' in url_part:
                raise NotImplementedError("the extra file URL cannot include '<'")
            if kind == 'content':
                self.url_map.add(Rule(
                    f'/{url_part}',
                    endpoint='content',
                    defaults={'content': content_or_path},
                ))
            elif kind == 'path':
                self.url_map.add(Rule(
                    f'/{url_part}',
                    endpoint='path',
                    defaults={'path': content_or_path, 'subpath': None},
                ))
                self.url_map.add(Rule(
                    f'/{url_part}/<path:subpath>',
                    endpoint='path',
                    defaults={'path': content_or_path},
                ))
            else:
                raise ValueError(kind)

        self.static_mode = config.get('static_mode', False)

    async def __call__(self, scope, receive, send) -> None:
        await self.get_app(scope, receive, send)

    def get_app(self, scope, receive, send):
        if scope['method'] != 'GET':
            # The Freezer only sends GET requests.
            # When we get another method, we know it came from another WSGI
            # server. Handle it specially.
            return self.handle_non_get(scope, receive, send)

        if self.static_mode:
            # Construct a new scope, only keeping the info that a server
            # of static pages would use
            COPIED_KEYS = {
                'type',
                'asgi',
                'http_version',
                'method',
                'root_path',
                'path',
                # query_string (URL parameters) is missing
                # headers is missing
                'server',
                'freezeyt.freezing',
                'freezeyt.task',  # (hack, TODO: remove)
            }
            new_scope = {
                **{
                    key: scope[key] for key
                    in COPIED_KEYS.intersection(scope)
                },
            }
            scope = new_scope

        # path_info = environ.get('PATH_INFO', '')

        server = scope.get('server')
        if server:
            hostname, port = server
        elif self.prefix:
            hostname = self.prefix.hostname
        else:
            hostname = 'unknown-host.invalid'
        prefix_path = scope.get('root_path', '')
        if not prefix_path.endswith('/'):
            prefix_path += '/'
        path_info = scope['path']
        if path_info.startswith(prefix_path):
            path_info = "/" + path_info[len(prefix_path):]
        map_adapter = self.url_map.bind(
            server_name=hostname,
            script_name=prefix_path,
            path_info=path_info,
        )
        try:
            endpoint, args = map_adapter.match()
        except NotFound:
            endpoint = 'app'
            args = {}
        except RequestRedirect as redirect:
            return asgi_app(
                scope, receive, send,
                (b'location', redirect.new_url.encode()),
                status=308,  # permanent redirect
            )

        if endpoint == 'content':
            mimetype = self.mimetype_checker.guess_mimetype(path_info)
            return asgi_app(
                scope, receive, send,
                (b'content-type', mimetype.encode()),
                body=args['content'],
            )
        if endpoint == 'path':
            base_path = args['path']
            extra_path = args['subpath']
            if extra_path:
                file_path = safe_join(str(base_path), str(extra_path))
                if file_path is None:
                    return asgi_app(
                        scope, receive, send,
                        status=403,  # Forbidden
                        body=b"403 Forbidden",
                    )
            else:
                file_path = base_path
            assert file_path is not None
            # TODO: use PathSend extension: https://asgi.readthedocs.io/en/latest/extensions.html#path-send
            try:
                file = open(file_path, 'rb')
            except FileNotFoundError:
                return asgi_app(
                    scope, receive, send,
                    status=404,  # not found
                )
            except OSError:
                # This could have several different behaviors,
                # see https://github.com/encukou/freezeyt/issues/331
                # For now, return a 404
                return asgi_app(
                    scope, receive, send,
                    status=404,  # not found
                )
            mimetype = self.mimetype_checker.guess_mimetype(path_info)
            return send_file(scope, receive, send, file=file, mimetype=mimetype)

        asgi_headers = None
        async def checking_send(event):
            nonlocal asgi_headers
            await send(event)
            if event["type"] == "http.response.start":
                asgi_headers = event.get("headers", [])
            elif event["type"] == "http.response.body":
                wsgi_headers = [(k.decode(), v.decode()) for k, v in asgi_headers]
                self.mimetype_checker.check(path_info, wsgi_headers)

        return self.app(scope, receive, checking_send)

    def handle_non_get(self, scope, receive, send):
        # Handle requests other than GET. These can't come from Freezeyt.
        if not self.static_mode:
            # Normally, pass all other requests to the app unchanged.
            return self.app(scope, receive, send)

        # In static mode, disallow everything but GET, HEAD, OPTIONS.

        if scope['method'] == 'HEAD':
            # For HEAD, call the app but ignore the response body
            new_scope = {**scope, 'method': 'GET'}
            async def filtered_send(event):
                if event['type'] == "http.response.start":
                    await send(event)
                    await send({'type': "http.response.body"})
            return self.app(new_scope, receive, filtered_send)
        elif scope['method'] == 'OPTIONS':
            # For OPTIONS, give our own response
            # (The status should be '204 No Content', but according to
            # MDN, some browsers misinterpret that, so '200' is safer.)
            return asgi_app(
                scope, receive, send,
                (b'allow', b'GET, HEAD, OPTIONS'),
            )
        else:
            # Disallow other methods
            return asgi_app(
                scope, receive, send,
                status=405,  # Method not allowed
            )

async def asgi_app(
    scope, receive, send,
    *headers,
    status=200,
    body=b'',
):
    while True:
        event = await receive()
        if event['type'] == "http.request":
            await send({
                "type": "http.response.start",
                "status": status,
                "headers": headers,
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            return


async def send_file(scope, receive, send, *, file, mimetype):
    while True:
        event = await receive()
        if event['type'] == "http.request":
            await send({
                "type": "http.response.start",
                "status": 200,  # OK
                "headers": [(b'Content-Type', mimetype.encode())],
            })
            with file:
                while True:
                    chunk = file.read(FILE_CHUNK_SIZE)
                    if chunk:
                        await send({
                            "type": "http.response.body",
                            "body": chunk,
                            "more_body": True,
                        })
                    else:
                        await send({
                            "type": "http.response.body",
                        })
                        return
