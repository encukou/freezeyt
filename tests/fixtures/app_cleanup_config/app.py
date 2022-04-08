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
            <h3>Hello world! This is Falcon app page with link to value_error page.</h3>
            <a href="/value_error.html">value_error.html</a>
        </body>
    </html>\n"""

    def on_get_error(self, req, resp):
        """Handles GET requests on index (/value_error.html)"""
        raise falcon.HTTPNotFound()


# create Falcon App for testing purposes
app = falcon.App(media_type=falcon.MEDIA_HTML)    
resource = Resource()
app.add_route('/', resource)
app.add_route('/value_error.html', resource, suffix="error")