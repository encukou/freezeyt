from urllib.parse import unquote

# See doc/encoding-notes.txt for notes on the string encodings.

def decode_input_path(s):
    r"""Decodes a path from URL (text) for internal use

    Examples:
        /čau/☺フ → /čau/☺フ
        /%C4%8Dau → /čau
        /%8Dau → '/\udc8dau'
    """
    return unquote(s, errors='surrogateescape')


def encode_wsgi_path(s):
    """Encodes an URL path from internal format for use in WSGI"""

    bytestring = s.encode('utf-8', errors='surrogateescape')
    return bytestring.decode('latin-1')


def encode_file_path(s):
    """Encodes an URL path from internal format for use in disk filenames"""
    # This doesn't change the string.
    # But, if we ever change the internal representation of paths, we'll
    # need to change the 3 functions here that deal with it
    return s
