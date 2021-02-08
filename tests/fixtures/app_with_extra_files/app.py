from pathlib import Path

from flask import Flask

APP_DIR = Path(__file__).parent

app = Flask(__name__)
freeze_config = {'extra_files':
                    {   'CNAME': 'pylades.cz',
                        '.nojekyll': '',
                        'config/xyz': 'abc',
                        'smile.png': b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\x08\0\0\0\x08\x08\x04\0\0\0n\x06v\0\0\0\0#IDAT\x08\xd7cd``\xf8\xcf\x80\0\x8c\xa8\\ \x8f\tB!\x91D\xab\xf8\x8f\x10D\xd3\xc2\x88n-\0\x0e\x1b\x0f\xf9LT9_\0\0\0\0IEND\xaeB`\x82',
                        'bin_range.dat': {'base64': 'AAECAwQFBgcICQ=='},
                        'smile2.png': {'copy_from': str(APP_DIR / 'smile2.png')},
                    }
                }


@app.route('/')
def index():
    """Create the index page of the web app."""
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """


expected_dict = {
    'index.html':
        b'\n    <html>\n        <head>\n            <title>Hell'
        + b'o world</title>\n        </head>\n        <body>\n'
        + b'            Hello world!\n        </body>\n    </html>\n    ',

    'CNAME':
        b'pylades.cz',

    '.nojekyll':
        b'',

    'config': {
        'xyz':
            b'abc'
    },

    'smile.png':                            b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\x08\0\0\0\x08\x08\x04\0\0'
    + b'\0n\x06v\0\0\0\0#IDAT\x08\xd7cd``\xf8\xcf\x80\0\x8c\xa8\\ '
    + b'\x8f\tB!\x91D\xab\xf8\x8f\x10D\xd3\xc2\x88n-\0\x0e\x1b\x0f'
    + b'\xf9LT9_\0\0\0\0IEND\xaeB`\x82',

    'bin_range.dat': b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09',

    'smile2.png':                            b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\x08\0\0\0\x08\x08\x04\0\0'
    + b'\0n\x06v\0\0\0\0#IDAT\x08\xd7cd``\xf8\xcf\x80\0\x8c\xa8\\ '
    + b'\x8f\tB!\x91D\xab\xf8\x8f\x10D\xd3\xc2\x88n-\0\x0e\x1b\x0f'
    + b'\xf9LT9_\0\0\0\0IEND\xaeB`\x82',
}
