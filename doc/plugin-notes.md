# Freezeyt plugins (WIP)

## Progressbar

```python
class FreezeytProgress:
    def __init__(self):
        self.progress = tqdm()
        self.current_pos = 0

    def update(self, current, total):
        self.progress.total = total
        self.progress.update(current - self.current_pos)
        self.current_pos = current

    def close(self):
        self.progress.close()

config['progress'] = FreezeytProgress()
```

## Option to save to files, dict or Git

```python
class FileSaver:
    def __init__(self, base_path, prefix):
        self.base_path = base_path
        self.prefix = prefix

    def url_to_filename(self, url):
        ...

    def save(self, url, content_iterable):
        filename = self.url_to_filename(url)
        with open(filename, "wb") as f:
            for item in content_iterable:
                f.write(item)

    def open(self, url):
        filename = self.url_to_filename(url)
        return open(filename, 'rb')

config['save'] = FileSaver()
```

```python
class FileSaver:
    def __init__(self, base_path, prefix):
        self.base_path = base_path
        self.prefix = prefix
        self.dict = {}

    def url_to_keys(self, url):
        ...

    def save(self, url, content_iterable):
        keys = self.url_to_filename(url)
        current_dict = self.dict
        for key in keys[:-1]:
            current_dict = current_dict.setdefault(key, {})
        current_dict[keys[-1]] = ''.join(content_iterable)

    def open(self, url):
        current_dict = self.dict
        for key in keys:
            current_dict = current_dict.setdefault(key, {})
        return BytesIO(current_dict)
```

## Choice of MIME type database

```python
class MimeValidator:
    def validate(self, url, headers, open_output):
        # (see check_mimetype)

config['validators'].append(MimeValidator())
```

## Page validation

```python
class HtmlValidator:
    def validate(self, url, headers, open_output):
        with open_output() as file:
            html = parse_html()
            if not valid(html):
                raise ValueError("invalid HTML")

config['validators'].append(HtmlValidator())
```

## Harvesting links

```python
class GetLinksFromHTML:
    def get_links(self, url, headers, open_output):
        cont_type, cont_encode = parse_options_header(response_headers.get('Content-Type'))
        if cont_type == 'text/html':
            links = []
            ...
            return links

config['get_links'] = GetLinksFromHTML()
```

## Static files directory
