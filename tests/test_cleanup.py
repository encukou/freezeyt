import falcon
from freezeyt import freeze
from testutil import raises_multierror_with_one_exception


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
        raise ValueError()


# create Falcon App for testing purposes
app = falcon.App(media_type=falcon.MEDIA_HTML)    
resource = Resource()
app.add_route('/', resource)
app.add_route('/value_error.html', resource, suffix="error")


def test_let_incomplete_dir_intact(tmp_path):
    output_dir = tmp_path / "output"
    config = {"cleanup": False, "output": str(output_dir)}
    with raises_multierror_with_one_exception(ValueError):
        freeze(app, config)
    assert output_dir.exists() == True # the output dir has to exist
    assert (output_dir / "index.html").exists() == True # the index.html file inside output dir has to exist


def test_remove_incomplete_dir(tmp_path):
    output_dir = tmp_path / "output2"
    config = {"cleanup": True, "output": str(output_dir)}
    with raises_multierror_with_one_exception(ValueError):
        freeze(app, config)
    assert output_dir.exists() == False # the output dir has to be gone


def test_remove_incomplete_dir_by_default(tmp_path):
    output_dir = tmp_path / "output3"
    config = {"output": str(output_dir)}
    with raises_multierror_with_one_exception(ValueError):
        freeze(app, config)
    assert output_dir.exists() == False # the output dir has to be gone

