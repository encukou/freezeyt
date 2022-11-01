import base64
from pathlib import Path, PurePosixPath

def get_extra_files(config):
    extra_files_config = config.get('extra_files')
    if extra_files_config is not None:
        for url_part, content in extra_files_config.items():
            if isinstance(content, str):
                content = content.encode()
            elif isinstance(content, dict):
                if 'base64' in content:
                    content = base64.b64decode(content['base64'])
                elif 'copy_from' in content:
                    path = Path(content['copy_from'])
                    yield from get_extra_files_from_path(
                        url_path=PurePosixPath(url_part),
                        disk_path=path,
                    )
                    continue
                else:
                    raise ValueError(
                        'a mapping in extra_files must contain '
                        + '"base64" or "copy_from"'
                    )
            yield url_part, content

def get_extra_files_from_path(url_path, disk_path):
    if disk_path.is_dir():
        for subpath in disk_path.iterdir():
            yield from get_extra_files_from_path(
                url_path / subpath.name, subpath)
    else:
        yield str(url_path), disk_path.read_bytes()
