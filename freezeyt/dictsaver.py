from io import BytesIO
from pathlib import Path

from freezeyt.util import is_external
from freezeyt.encoding import encode_file_path


class DictSaver:
    """Outputs frozen pages into a dict.

    prefix - Base URL to deploy web app in production
        (eg. url_parse('http://example.com:8000/foo/')
    """
    def __init__(self, prefix):
        self.prefix = prefix
        self.contents = {}

    def url_to_parts(self, parsed_url):
        """Return filename parts to which the page is frozen.

        Parameters:
        parsed_url
            Parsed URL (eg. url_parse(http://example.com:8000/foo/second.html))
            to convert to filename

        Returns a tuple like ('foo', 'second.html')
        """
        if is_external(parsed_url, self.prefix):
            raise ValueError(f'external url {parsed_url}')

        url_path = parsed_url.path

        if url_path.startswith(self.prefix.path):
            url_path = '/' + url_path[len(self.prefix.path):]

        if url_path.endswith('/'):
            url_path = url_path + 'index.html'

        return tuple(encode_file_path(url_path).lstrip('/').split('/'))

    def prepare(self):
        """DictSaver doesn't need any preparation"""

    def save_to_filename(self, filename, content_iterable):
        parts = Path(filename).parts
        self._save_to_parts(parts, content_iterable)

    def save(self, parsed_url, content_iterable):
        parts = self.url_to_parts(parsed_url)
        self._save_to_parts(parts, content_iterable)

    def _save_to_parts(self, parts, content_iterable):
        print(f'Saving to {parts}')
        target = self.contents
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = b''.join(content_iterable)

    def open(self, parsed_url):
        parts = self.url_to_parts(parsed_url)
        target = self.contents
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        return BytesIO(target[parts[-1]])

    def get_result(self):
        return self.contents
