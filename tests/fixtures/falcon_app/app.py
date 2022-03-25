import falcon
from pathlib import Path

STATIC_IMAGE_PATH = Path(__file__).parent / 'static'

class Resource(object):
    def on_get(self, req, resp):
        """Handles GET requests on index (/)"""
        resp.text = """
    <html>
        <head>
            <title>Hello world from Falcon app</title>
        </head>
        <body>
            <h3>Hello world! This is a home page of Falcon app.</h3>
            <div>
            <a href='/second_page/'>LINK</a> to second page.
            </div>
        </body>
    </html>\n"""
    
    def on_get_second(self, req, resp):
        """Handles GET requests on index (/second_page/)"""
        resp.text = """
    <html>
        <head>
            <title>Hello world from Falcon app</title>
        </head>
        <body>
            <h3>Hello world! This is a second page of Falcon app.</h3>
            <a href='/image_page/'>LINK to image page</a>
        </body>
    </html>\n"""
    
    def on_get_image(self, req, resp):
        resp.text = """
    <html>
        <head>
            <title>Hello world from Falcon app</title>
        </head>
        <body>
            <h3>Hello world! This is a image page of Falcon app.</h3>
            <img src="/images/smile.png" alt="smile">
            <a href="/">LINK to homepage</a>
        </body>
    </html>\n"""

app = falcon.App(media_type=falcon.MEDIA_HTML)
app.add_static_route("/images", STATIC_IMAGE_PATH, downloadable=True, fallback_filename=None)

resource = Resource()
app.add_route('/', resource)
app.add_route('/second_page/', resource, suffix="second")
app.add_route('/image_page/', resource, suffix="image")

expected_dict = {
    'index.html':
        b"\n    <html>\n        <head>\n            "
        + b"<title>Hello world from Falcon app</title>\n        </head>\n        <body>\n"
        + b"            <h3>Hello world! This is a home page of Falcon app.</h3>\n"
        + b"            <div>\n            <a href='/second_page/'>LINK"
        + b"</a> to second page.\n            </div>\n        </body>\n"
        + b"    </html>\n",

    'second_page': {'index.html':
        b"\n    <html>\n        <head>\n            "
        + b"<title>Hello world from Falcon app</title>\n        </head>\n        <body>\n"
        + b"            <h3>Hello world! This is a second page of Falcon app.</h3>\n"
        + b"            <a href='/image_page/'>LINK to image page</a>\n"
        + b"        </body>\n"
        + b"    </html>\n"},

    'images': {
        'smile.png': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x08\x00\x00\x00\x08\x08\x06\x00\x00\x00\xc4\x0f\xbe\x8b\x00\x00\x01\x85iCCPICC profile\x00\x00(\x91}\x91=H\xc3@\x1c\xc5_[\xa5\xa5T\x14,"\xe2\x90\xa1:Y\x10\xbfp\xd4*\x14\xa1B\xa8\x15Zu0\xb9\xf4Ch\xd2\x90\xa4\xb88\n\xae\x05\x07?\x16\xab\x0e.\xce\xba:\xb8\n\x82\xe0\x07\x88\x93\xa3\x93\xa2\x8b\x94\xf8\xbf\xa4\xd0"\xc6\x83\xe3~\xbc\xbb\xf7\xb8{\x07\xf8\xebe\xa6\x9a\x1d\xa3\x80\xaaYF:\x99\x10\xb2\xb9\x15!\xf8\x8a\x10\xc2\xe8\xc1$\xfa$f\xea\xb3\xa2\x98\x82\xe7\xf8\xba\x87\x8f\xafwq\x9e\xe5}\xee\xcf\xd1\xa5\xe4M\x06\xf8\x04\xe2\x19\xa6\x1b\x16\xf1:\xf1\xd4\xa6\xa5s\xde\'\x8e\xb2\x92\xa4\x10\x9f\x13\x8f\x18tA\xe2G\xae\xcb.\xbfq.:\xec\xe7\x99Q#\x93\x9e#\x8e\x12\x0b\xc56\x96\xdb\x98\x95\x0c\x95x\x828\xa6\xa8\x1a\xe5\xfb\xb3.+\x9c\xb78\xab\xe5*k\xde\x93\xbf0\x92\xd7\x96\x97\xb8Ns\x10I,`\x11"\x04\xc8\xa8b\x03eX\x88\xd3\xaa\x91b"M\xfb\t\x0f\xff\x80\xe3\x17\xc9%\x93k\x03\x8c\x1c\xf3\xa8@\x85\xe4\xf8\xc1\xff\xe0w\xb7fa|\xccM\x8a$\x80\xce\x17\xdb\xfe\x18\x02\x82\xbb@\xa3f\xdb\xdf\xc7\xb6\xdd8\x01\x02\xcf\xc0\x95\xd6\xf2W\xea\xc0\xf4\'\xe9\xb5\x96\x16;\x02\xba\xb7\x81\x8b\xeb\x96&\xef\x01\x97;@\xff\x93.\x19\x92#\x05h\xfa\x0b\x05\xe0\xfd\x8c\xbe)\x07\xf4\xde\x02\xe1U\xb7\xb7\xe6>N\x1f\x80\x0cu\x95\xba\x01\x0e\x0e\x81\xe1"e\xafy\xbc;\xd4\xde\xdb\xbfg\x9a\xfd\xfd\x00z~r\xaa\x113\xb8=\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00.#\x00\x00.#\x01x\xa5?v\x00\x00\x00\x07tIME\x07\xe4\x08\n\x107\x0euUv\xd2\x00\x00\x00\x19tEXtComment\x00Created with GIMPW\x81\x0e\x17\x00\x00\x00eIDAT\x18\xd3}\xcf\xb1\r\x83P\x10\x03\xd0\xf7\xbf\x18\x83&]\xb2\x05\x15\x15M\xf6HA\xc1 \x14\xec\x91\x9ea`\x14(\xf8QN\x11\xc4\x8d\xed\xbb\x93\xe5K\x0et\xa8\xb1\xf9b\xc5\x0c\x8dk\xb4\x19\xf7b\xdea1\x15\xbe\xe50|\x06\xfd*\x9c\xe2A\x7f\x92\xa0\n\xc5F\x0c\xc81\x01\xda?%\x9b\xf4\x11x\xfc\xbc\xb9`\xde\x01Qk\x0c\xd9>\xf6\x12\xa2\x00\x00\x00\x00IEND\xaeB`\x82',
    },

    'image_page': {'index.html':
        b'\n'
        + b'    <html>\n'
        + b'        <head>\n'
        + b'            <title>Hello world from Falcon app</title>\n'
        + b'        </head>\n'
        + b'        <body>\n'
        + b'            <h3>Hello world! This is a image page of Falcon app.</h3>\n'
        + b'            <img src="/images/smile.png" alt="smile">\n'
        + b'            <a href="/">LINK to homepage</a>\n'
        + b'        </body>\n'
        + b'    </html>\n'},

}

# this part of code will not affect tests but you can run standalone Falcon app with it
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server('', 8000, app) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()

# SOME NOTES:

# if you need to check dictionary output, you can do that with this code:
# from freezeyt import freeze
# new_dict = freeze(app, {"output": {"type": "dict"}})
