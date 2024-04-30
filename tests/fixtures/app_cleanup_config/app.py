import falcon

freeze_config = {'cleanup': False}

class Resource(object):
    """Creates Resource object for Falcon App"""
    def on_get(self, req, resp):
        """Handles GET requests on index (/)"""
        resp.text = """
    <html>
        <head>
            <title>Hello world from Falcon app</title>
        </head>
        <body>
            <h3>Hello world! This is Falcon app page link to error 404.</h3>
            <a href="/not_found.html">not_found.html</a>
        </body>
    </html>\n"""

    on_head = on_get

    def on_get_error(self, req, resp):
        """Handles GET requests on index (/not_found.html)"""
        raise falcon.HTTPNotFound()

    on_head_error = on_get_error

# create Falcon App for testing purposes
app = falcon.App(media_type=falcon.MEDIA_HTML)    
resource = Resource()
app.add_route('/', resource)
app.add_route('/not_found.html', resource, suffix="error")

