
from freezeyt.util import is_external
from freezeyt.encoding import encode_file_path


class DirectoryExistsError(Exception):
    """Attempt to overwrite directory that doesn't contain freezeyt output"""


class FileSaver:
    """Outputs frozen pages as files on the filesystem.

    base - Filesystem base path (eg. /tmp/)
    prefix - Base URL to deploy web app in production
        (eg. urlparse('http://example.com:8000/foo/')
    """
    def __init__(self, base_path, prefix):
        self.base_path = base_path
        self.prefix = prefix

        exists = self.base_path.exists()
        has_files = list(self.base_path.iterdir())
        has_index = self.base_path.joinpath('index.html').exists()
        if exists and has_files and not has_index:
            raise DirectoryExistsError(
                f'Will not overwrite directory {base_path}: it '
                + f'contains files that do not look like a frozen website. '
                + f'If you are sure, remove the directory before running '
                + f'freezeyt.'
            )

    def url_to_filename(self, parsed_url):
        """Return the filename to which the page is frozen.

        Parameters:
        parsed_url
            Parsed URL (eg. urlparse(http://example.com:8000/foo/second.html))
            to convert to filename
        """
        if is_external(parsed_url, self.prefix):
            raise ValueError(f'external url {parsed_url}')

        url_path = parsed_url.path

        if url_path.startswith(self.prefix.path):
            url_path = '/' + url_path[len(self.prefix.path):]

        if url_path.endswith('/'):
            url_path = url_path + 'index.html'

        return self.base_path / encode_file_path(url_path).lstrip('/')

    def save_to_filename(self, filename, content_iterable):
        absolute_filename = self.base_path / filename
        self._save(absolute_filename, content_iterable)

    def save(self, parsed_url, content_iterable):
        absolute_filename = self.url_to_filename(parsed_url)
        self._save(absolute_filename, content_iterable)

    def _save(self, absolute_filename, content_iterable):
        print(f'Saving to {absolute_filename}')
        absolute_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(absolute_filename, "wb") as f:
            for item in content_iterable:
                f.write(item)

    def open(self, parsed_url):
        filename = self.url_to_filename(parsed_url)
        return open(filename, 'rb')
