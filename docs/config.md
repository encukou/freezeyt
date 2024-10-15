# Configuration {: #configuration }

Freezeyt is primarily configured using a dictionary of options,
usually loaded from a YAML (or JSON) file given on the command line (CLI)
using the `-c/--config` argument, for example:

```console
$ python -m freezeyt my_app _build -c freezeyt.yaml
```

See [below](#example) for an example of what goes in the file.

Instead of a file, you can also put the configuration in a Python
dictionary and tell Freezeyt to import it using the `-C/--import-config`
argument.
Like the application to freeze, the argument takes the name of an importable
module and the name of a variable in that module, separated by a colon.
For example:

```console
$ python -m freezeyt my_app _build -C my_app:freezeyt_config
```

## CLI

Most command-line arguments correspond directly to an configuration option.
Unless documented otherwise, CLI arguments will override values
from a file or dictionary.

Here is a full list of CLI arguments:

| CLI argument | Option name |  Meaning |
|----------|------------|----------|
| APP (positional) | `app` | [Application to freeze](#conf-app) |
| `-o`, `--output`, positional | `output` | [Output directory](#conf-output) |
| `-c`, `--config` | --- | [Configuration file](#configuration) |
| `-C`, `--import-config` | --- | [Configuration variable](#configuration) |
| `--prefix` | `prefix` | [URL prefix](#conf-prefix) |
| `--extra-page` | `extra_pages`  | [Extra pages](#conf-extra_pages) |
| `--progress` | (plugins) | [Progress bar and logging](#conf-cli-progress) |
| `--gh-pages` | `gh_pages` | [Github Pages Plugin](#conf-gh_pages) |
| `--no-cleanup` | `cleanup` | Don't [clean up](#conf-cleanup) |
| `-x`, `--fail-fast` | `fail_fast` | [Fail fast](#conf-fail_fast) |
| `--help` | --- | Show help and exit |

## Example {: #example }

Here's an example YAML configuration file.
See below for descriptions of the individual options.

```yaml
output: ./_build/   # The website will be saved to this directory
prefix: https://mysite.example.com/subpage/
extra_pages:
    # Let Freezeyt know about URLs that are not linked from elsewhere
    /robots.txt
    /easter-egg.html
extra_files:
    # Include additional files in the output:
    # Static files
    static:
        copy_from: static/
    # Web host configuration
    CNAME: mysite.example.com
    ".nojekyll": ''
    googlecc704f0f191eda8f.html:
        copy_from: google-verification.html
status_handlers:
    # If a redirect page (HTTP status 3xx) is found, warn but don't fail
    "3xx": warn
```

## Overview of the options

The following options are configurable:

| Option name | Meaning | Example |
|----------|---------|---------|
| `app` | [Application to freeze](#conf-app) | `'module:wsgi_app'` |
| `output` | [Output directory](#conf-output) | `'./_build/'` |
| `prefix` | [URL prefix](#conf-prefix) | `'https://mysite.example.com/subpage/'` |
| `extra_pages` | [Extra pages](#conf-extra_pages) | (list) |
| `extra_files` | [Extra files](#conf-extra_files) | (dict) |
| `cleanup` | [Clean up](#conf-cleanup) | `False` |
| `fail_fast` | [Fail fast](#conf-fail_fast) | `True` |
| `gh_pages` | [Github Pages Plugin](#conf-gh_pages) | `True` |
| `default_mimetype` | [Default MIME type](#conf-default_mimetype) | `text/plain` |
| `get_mimetype` | [MIME type getter](#conf-default_mimetype) | `module:your_function` |
| `mime_db_file` | [MIME type database](#conf-mime_db_file) | `path/to/mime-db.json` |
| `version` | [Configuration version](#conf-version) | `1` |
| `plugins` | [Plugins](#conf-plugins) | (dict) |
| `hooks` | [Hooks](#conf-hooks) | (dict) |
| `status_handlers` | [HTTP Status handling](#conf-status_handlers) | (dict) |
| `url_finders` | [URL finders](#conf-url_finders) | (dict) |
| `use_default_url_finders` | [Use default URL finders](#conf-use_default_url_finders) | `False` |
| `urls_from_link_headers` | [Find URLs in Link headers](#conf-urls_from_link_headers) | `False` |
| `url_to_path` | [Path generation](#conf-url_to_path) | `my_module:url_to_path` |
| `static_mode` | [Middleware static mode](#conf-static_mode) | `True` |


## Basic options


### Configuration version  {: #conf-version }

To ensure that your configuration will work unchanged in newer versions of Freezeyt,
you should add the current version number, `1`, to your configuration like this:

```yaml
version: 1
```

This is not mandatory. If the version is not given, the configuration may
not work in future versions of Freezeyt.


### Application to freeze  {: #conf-app }

The name of importable Python module that contains the application must be
given in the configuration, or on the command line as first argument.

Inside the module, Freezeyt looks for the variable *app* by default.
A different variable can be specified after the module name, separated by
a colon (`:`).
When the module is specified both on the command line and in the config file,
an error is raised.

When the configuration is a Python dict, `app` can be given directly as
the WSGI application object, rather than a string.

#### Examples

Freezeyt looks for the variable `app` inside the module by default.
In YAML, it looks like this:

```yaml
app: app_module
```

If `app` is in a submodule, separate package names with a dot:
```yaml
app: app_package.wsgi
```

A different variable name can be specified by using `:`.
```yaml
app: app_module:wsgi_application
```

In Python, the app can be given directly:

```python
my_app = Flask(__name__)
...

freezeyt_config = {'app': my_app}
```

### Output  {: #conf-output }

The `output` option conifgures the output directory, where the
result is saved:

```yaml
output: ./_build/
```

Alternatively, the output directory can be specified on the command line,
either by the `--output` (`-o`) argument or as a second positional argument.

The output must be specified in only one way; providing both the config
option and CLI argument is an error.

If there is any existing content in the output directory,
Freezeyt will either remove it (if the content looks like a previously
frozen website) or raise an error.
Best practice is to remove the output directory before freezing.

#### Output to dictionary

*Freezeyt* can return the result in a dictionary,
rather than save it to disk.
Note that this stores the entire frozen website in memory,
so it is mostly useful for testing.
This can be configured by setting `output` to the dictionary
`{'type': 'dict'}`, rather than to a string:

```yaml
output:
    type: dict
```

In this case, the `freeze()` function returns a dictionary of filenames
and their contents.
For example, a site with `/`, `/second_page/` and `/images/smile.png`
will be represented as:

```python
{
    'index.html': b'<html>...',
    'second_page': {
        'index.html': b'<html>...',
    },
    'images': {
        'smile.png': b'\x89PNG\r\n\x1a\n\x00...',
    },
}
```

#### Explicitly output to disk

It is possible to explicitly request Freezeyt to output to a directory
using a dict like this:

```yaml
output:
    type: dir
    dir: ./_build/
```

This is equivalent to the string `./_build/`, or passing `./_build/` as the
CLI argument.

There are currently no output types other that `dir` and `dict`.


### URL prefix  {: #conf-prefix }

The URL where the application will be deployed can be
specified with `prefix`, for example:

```yaml
prefix: http://localhost:8000/
```
or
```yaml
prefix: https://mysite.example.com/subpage/
```

The *prefix* URL must end with a slash.

The page at the *prefix* URL is considered the application's “home page”,
and will always be frozen.

Freezeyt considers all pages under the prefix to be part of
the application.
For example, with the second prefix above:

- `https://mysite.example.com/subpage/blog.html` would be followed,
  and the page would be frozen at `<output_directory>/blog.html`;
- `https://mysite.example.com/about.html` would be considered an external link,
  and ignored.

The prefix is also passed to the application as the server and script name,
which should be used whenever the app generates absolute URLs.

The prefix can also be specified on thecommand line with e.g.:
`--prefix=http://localhost:8000/`.
The CLI argument has priority over the config file.


## Extra content

Usually, Freezeyt saves pages that are reachable by links from the app's
home page.
There are two cases when this is not enough, and you need to specify
extra content manually:

- Extra *pages* are part of the application, but not reachable by following
  links. For example, a an old URL that redirects to a new location should
  be configured as an extra page. See [Known URLs][known-urls] for details.

- Extra *files* are not part of the application.
  Typically, these are used to configure the static page server, like
  a `CNAME` file GitHub's or `.htaccess` for Apache.


### Extra pages  {: #conf-extra_pages }

URLs of pages that are not reachable by following links from the homepage
can specified as “extra” pages in the configuration:

```yaml
extra_pages:
    - extra/
    - extra2.html
```

The URLs should be relative (to the [prefix](#conf-prefix)).
Absolute URLs are allowed, but they must start with the prefix.

Freezeyt will handle these pages as if it found them as links.
For example, by default it will follow links in extra pages.

Extra pages may also be given with the `--extra-page` command line argument,
which can be repeated (for example,
`--extra-page extra/ --extra-page extra2.html`).
The lists from CLI and the config file are merged together.

You can also specify extra pages using a Python function,
specified using a module name and function name as follows:

```yaml
extra_pages:
    - generator: my_app:generate_extra_pages
```

This function should take the application as argument and return an iterable
of URLs as strings.

When using the Python API, this function can be specified
directly as a Python object, for example:

```python
def generate_extra_pages(app):
    yield 'extra/'
    yield 'extra2.html'

config = {
   ...
   'extra_pages': [{'generator': generate_extra_pages}],
}
another_config = {
   ...
   'extra_pages': [generate_extra_pages],
}
```

### Extra files  {: #conf-extra_files }

Extra files to be included in the output can be specified,
along with their content.

For example, the following config will add 3 files to the output:

```yaml
extra_files:
    CNAME: mysite.example.com
      ".nojekyll": ''
    config/xyz: abc
```

The files will be:

- `<output directory>/CNAME`, with the content `mysite.example.com`;
- `<output directory>/.nojekyll`, empty;
- `<output directory>/config/xyz`, with the content `abc`.

These files are not considered part of the application.
*Freezeyt* will not retrieve them from the app, and it will not try to find
links in them.

Extra files are mainly useful for configuration of your static server.
For files that are part of the website,
such as a [favicon](https://en.wikipedia.org/wiki/Favicon), we recommend
adding them to your application, and either link to them or add them as
[extra *pages*](#conf-extra_pages).

You can also specify extra file content using the Base64 encoding (`base64`) or
as a filesystem path to be copied (`copy_from`), like so:

```yaml
extra_files:
    config.dat:
        base64: "YWJjZAASNA=="
    config2.dat:
        copy_from: included/config2.dat
```

If the `copy_from` path names a directory, it will be copied recursively.

In the file name, Freezeyt treats both backslashes and forward slashes
as path separators.

Extra files cannot be specified on the CLI.


## Debugging options

The following options are useful when debugging your application,
or its integration with Freezeyt.


### Clean up  {: #conf-cleanup }

By default, if an error occurs during freezing, Freezeyt will delete
the incomplete output directory.
This is meant to prevent uploading incomplete results to web hosting by mistake.

If you want to keep the incomplete directory (for example,
to help debugging), you can use the `--no-cleanup` command line switch
or the `cleanup` configuration option:

```shell
$ freezeyt app -o ./build/ --no-cleanup
```

```yaml
cleanup: False
```

The command line switch has priority over the configuration.
Use `--cleanup` to override `cleanup: False` from the config.


### Fail fast  {: #conf-fail_fast }

By default, Freezeyt collects errors it finds on individual pages,
and presents them all when done.
To stop the process early when the first error occurs, use the
the `--fail-fast` (`-x`) command line switch or the `fail_fast` configuration option:

```shell
$ freezeyt app -o ./build/ --fail-fast
```

```yaml
fail_fast: True
```

The command line switch has priority over the configuration.
Use `--no-fail-fast` to override `fail_fast: True` from the config.


## Customizing the process

Here are ways to configure details of how Freezeyt saves pages.


### MIME type checking

For static sites to be served correctly on most servers, the MIME
`Content-Type` of a page must match the saved file's extension.
See [MIME type mapping][mime-type-mapping] for details.

To ensure that the application will work as intended when frozen and served
with such a server, Freezeyt verifies that the extensions of saved files
correspond to the MIME types served by the app.
This funtionality is provided by [`freezeyt.Middleware`][freezeyt.Middleware].

The exact mapping between extensions and `Content-Type` values varies
between servers.
*Freezeyt* uses Python's `mimetypes` module by default, but provides
several ways to customize it.

#### Default MIME type  {: #conf-default_mimetype }

Files without an extension are, by default, served as `application/octet-stream`
(arbitrary binary data).
This can be configured using the `default_mimetype` option.
For example, if your static page server defaults to plain text files,
use:

```yaml
default_mimetype=text/plain
```


#### MIME type getter  {: #conf-get_mimetype }

The most flexible way to map file extensions to MIME types is with
a custom function, which you can specify using the `get_mimetype` option.
For example:

```yaml
get_mimetype=module:your_function
```

`get_mimetype` can be defined as a string in the form `"module:function"`,
which names the function to call, or as a Python function
(if configuring Freezeyt using a Python dict).

The function will be called with one argument, the file path as a string, and
it should returns a list of corresponding MIME types
(for example, `["text/html"]` or `["audio/wav", "audio/wave"]`).

If `get_mimetype` instead returns `None`, Freezeyt will use the
[default MIME type](#conf-default_mimetype).

By default, Freezeyt calls the Python function
[`mimetypes.guess_type`](https://docs.python.org/3/library/mimetypes.html#mimetypes.guess_type)
and uses the `type` (the first element) of the result:

```python
def default_mimetype(url: str) -> Optional[List[str]]:
    file_mimetype, encoding = guess_type(url)
    if file_mimetype is None:
        # Freezeyt should use the default
        return None
    else:
        # A one-element list
        return [file_mimetype]
```


#### Using a mime-db database  {: #conf-mime_db_file }

There is an option to use [the MIME type database from the `jshttp` project](https://github.com/jshttp/mime-db/blob/master/db.json)
(the database used by GitHub Pages),
or a database with the same structure, for mapping file names to MIME types.

To use it, add the path to the JSON file to Freezeyt configuration:
```yaml
mime_db_file=path/to/mime-db.json
```
This is equivalent to setting `get_mimetype` to a function that maps
extensions to filetypes according to the database.


### URL finding  {: #conf-url_finders }

Freezeyt discovers new pages in the application by searching for URLs
in pages it processes. The search is done by *URL finders*,
functions that find URLs in a specific page type.

You can configure which finder is used for which MIME type using
the `url_finders` configuration key.
In the default configuration, Freezeyt finds links in HTML and CSS files.
The default could be configured like this:

```yaml
url_finders:
    text/html: freezeyt.url_finders:get_html_links
    text/css: freezeyt.url_finders:get_css_links
```

Keys in the `url_finders` dict are MIME types.
Values are functions, which can be defined as:

* Strings in the form `"module:function"`, which name the finder
  function to call.
* Python functions (if configuring Freezeyt from Python).
* Strings without a colon (`:`), which name a function from the
  `freezeyt.url_finders` module. Using this shortcut, the default configuration
  could also be written as:

        url_finders:
            text/html: get_html_links
            text/css: get_css_links


    The `freezeyt.url_finders` module includes these finders:

    - `get_html_links`, the default finder for HTML
    - `get_css_links`, the default finder for CSS
    - `get_html_links_async` and `get_css_links_async`, asynchronous variants
      of the above
    - `none`, a finder that doesn't find any links.

An URL finder function gets these arguments:

* The page content, as a binary file open for reading (for example,
  `io.BinaryIO`),
* the absolute URL of the page, as a `str`, and
* the HTTP headers, as a list of 2-tuples (as in WSGI).

The function should return an iterator of all URLs (as strings) found
in the page's contents, as they would appear in `href` or `src` attributes.
Specifically:

- The URLs can be relative.
- External URLs (i.e. those not beginning with the [`prefix`](#conf-prefix))
  should be included.

Finder functions may be asynchronous.
If the function returns a coroutine (for example, if it's defined with
`async def`, Freezeyt will use `await` on the result.
If the function returns an asynchronous generator (for example, if it's
defined with `async def` and uses `yield`), Freezeyt will use async iteration
to handle it.


#### URL finder header {: #conf-header-Freezeyt-URL-Finder }

You can specify a finder as a string in the `Freezeyt-URL-Finder` HTTP header.
If given, it overrides the `url_finders` configuration.

#### Default `get_html_links`

The default URL finder for HTML pages looks in `src` and `href` attributes
of all tags in the document.
It currently does not handle other links, such as embedded CSS, but it
may be improved in the future.

#### Default `get_css_links`

The default URL finder for CSS uses the [`cssutils`](https://pypi.org/project/cssutils/)
library to find all links in a stylesheet.
This may be changed in the future.

#### Disabling default URL finders  {: #conf-use_default_url_finders }

If a finder is not explictly specified in the configuration file,
Freezeyt will use the default. For example, if you specify
`text/html: my_custom_finder` only, Freezeyt will use the default finder
for `text/css`.

You can disable this behavior:

```yaml
use_default_url_finders: false
```


#### Finding URLs in Link headers  {: #conf-urls_from_link_headers }

By default, Freezeyt will follow URLs in `Link` HTTP headers.
To disable this, specify:

```yaml
urls_from_link_headers: false
```


### Freeze actions  {: #freeze-actions }

For each page it finds, Freezeyt will take an *action*: save the page,
ignore it, or treat it as an error.

By default, Freezeyt will save the pages with a `200 OK` HTTP status code,
and raise an error for any other status code.

You can configure the for an individual page from within the application
(or middleware), by setting the `Freezeyt-Action` HTTP header to one of
these strings:

* `'save'`: Freezeyt will save the body of the page.
* `'ignore'`: Freezeyt will not save any content for the page
* `'warn'`: will save the content and send warn message to stdout
* `'follow'`: Freezeyt will save content from the redirected location.
  This requires a `Location` header, which is usually added for redirects.
  Redirects to external pages are not supported.
* `'error'`: fail; the page will not be saved and `freeze()` will raise
  an exception.


#### HTTP Status handling  {: #conf-status_handlers }

If the `Freezeyt-Action` header is not set, Freezeyt will determine what to
do based on the HTTP status. The behavior can be customized using the
`status_handlers` setting.
For example, to ignore pages with the `404 NOT FOUND` status, rather than
treat them as errors, set the `404` handler to `'ignore'`:

```yaml
status_handlers:
    '404': ignore
```

More varied `status_handlers` could be specified as:

```yaml
status_handlers:
    '202': warn
    '301': follow
    '404': ignore
    '418': my_module:custom_action  # see below
    '429': ignore
    '5xx': error
```

Note that the status code must be a string.
In a YAML file, it needs to be quoted.

A range of statuses can be specified as one number (`1` to `5`) followed by
lowercase `xx`.
(Other "wildcards" like `50x` are not supported.)


[](){#custom-actions}
#### Custom freeze actions

You can also define a custom action in `status_handlers` as:

* a string in the form `'my_module:custom_action'`, which names a handler
  function to call, or
* a Python function (if configuring Freezeyt from Python).

The action function takes one argument a [`TaskInfo`][freezeyt.TaskInfo]
with information about the page being frozen.
Freezeyt's predefined actions, like `follow`, can be imported from
`freezeyt.actions`.
A custom action should call one of these default actions and return the return value from it.


### Path generation  {: #conf-url_to_path }

It is possible to customize the filenames that pages are saved under
using the `url_to_path` configuration key, for example:

```yaml
url_to_path: my_module:url_to_path
```

The value can be:

* A string in the form `"module:function"`, which names the
  function to call. The function can be omitted along with the colon,
  and defaults to `url_to_path`.
* A Python function, if configuring Freezeyt from Python.

The function receives one string: the *path* portion of the URL to save,
relative to the `prefix`.
It should return a path to the saved file, relative to the build directory,
as a string.

The default function, available as [`freezeyt.url_to_path`][freezeyt.url_to_path],
adds `"index.html"` if the URL ends with `/`.


### Plugins  {: #conf-plugins }

It is possible to extend Freezeyt with *plugins*,
either [“built-in” ones](#built-in-plugins) that ship with Freezeyt
or [external ones](#custom-plugins).

Plugins are added using configuration like:

```yaml
plugins:
    - freezeyt.plugins:ProgressBarPlugin
    - mymodule:my_plugin
```


## Built-in plugins  {: #built-in-plugins }


### Github Pages Plugin  {: #conf-gh_pages }

To make it easier to upload frozen pages to the [Github Pages service](https://pages.github.com/),
you can activate the GitHub Pages plugin using the `--gh-pages` CLI argument
or the `gh_pages` key in the configuration.
This creates a `gh-pages` git branch in the output directory.

By default, the Github Pages Plugin is not active. However, if you have
activated it in your configuration, you can override the choice in the CLI with
`--no-gh-pages`.

Configuration example:
```yaml
gh_pages: True
```

This is a shortcut for adding `freezeyt.plugins:GHPagesPlugin`
to [`plugins`](#conf-plugins).

To deploy a site to Github, you can then work with the git repository directly
in the output directory or pull the files into another repository/directory.
You can then pull/fetch files from the newly created `gh-pages` git branch in
many ways, for example:
```console
$ git fetch output_dir gh-pages
$ git branch --force gh-pages FETCH_HEAD
```
Note that this will overwrite the current contents of the `gh-pages` branch,
because of the `--force` switch.


### Progress bar and logging  {: #conf-cli-progress }

The CLI argument `--progress` controls what Freezeyt outputs as it
handles pages:

* `--progress=log`: Output a message about each frozen page to stdout.
* `--progress=bar`: Draw a status bar in the terminal. Messages about
  each frozen page are *also* printed to stdout, as with `log`.
* `--progress=none`: Don't do any of this.

The default is `bar` if stdout is a terminal, and `log` otherwise.

Alternately, it is possible to configure logging by adding one of the following
[`plugins`](#conf-plugins):

* `freezeyt.progressbar:ProgressBarPlugin`
* `freezeyt.progressbar:LogPlugin`


## Middleware static mode  {: #conf-static_mode }

When using the [Freezeyt middleware][middleware], you can enable *static mode*,
which simulates behaviour after the app is saved to static pages:

```yaml
static_mode: true
```

Currently, in static mode:

- HTTP methods other than GET and HEAD are disallowed.
- URL parameters are removed
- Request bodies are discarded
- Non-default WSGI environ keys are removed

Other restrictions and features may be added in the future, without regard
to backwards compatibility.
The static mode is intended for interactive use -- testing your app without
having to freeze all of it after each change.



## Extending Freezeyt


### Custom plugins  {: #custom-plugins }

A plugin is a function that Freezeyt will call before starting to
freeze pages.

It is passed a [`FreezeInfo`][freezeyt.FreezeInfo] object as argument.
Usually, the plugin will its [`add_hook`][freezeyt.FreezeInfo.add_hook] method
to register additional functions.


### Hooks  {: #conf-hooks }

It is possible to register *hooks*, functions that are called when
specific events happen in the freezing process.

For example, if `mymodule` defines functions `start` and `page_frozen`,
you can make Freezeyt call them using this configuration:

```yaml
hooks:
    start:
        - mymodule:start
    page_frozen:
        - mymodule:page_frozen
```

When configuring Freezeyt from Python, a function can be used directly
instead of a string.

The available hooks are:

#### `start`

Called when the freezing process starts, before any other hooks.

Takes one argument: a [`FreezeInfo`][freezeyt.FreezeInfo] object.


#### `page_frozen`

Called whenever a page is processed successfully.

Takes one argument: a [`TaskInfo`][freezeyt.TaskInfo] object.


#### `page_failed`

Called whenever a page is not saved due to an exception.

Takes one argument: a [`TaskInfo`][freezeyt.TaskInfo] object.


#### `success`

Called after the app is successfully frozen.

Takes one argument: a [`FreezeInfo`][freezeyt.FreezeInfo] object.
