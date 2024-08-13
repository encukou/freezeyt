# Configuration

Freezeyt is primarily configured using a dictionary of options,
usually loaded from a YAML (or JSON) file given on the command line (CLI)
using the `-c/--config` argument, for example:

```console
$ python -m freezeyt my_app _build -c freezeyt.yaml
```

See [below](#example) for an example of what goes in the file.

Instead of a file, you can also put the configuration in a Python
dictionary and tell *freezeyt* to import it using the `-C/--import-config`
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
| `-c`, `--config` | --- | [Configuration file](#conf-cli-config) |
| `-C`, `--import-config` | --- | [Configuration variable](#conf-cli-import-config) |
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
    # Let freezeyt know about URLs that are not linked from elsewhere
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

To ensure that your configuration will work unchanged in newer versions of freezeyt,
you should add the current version number, `1`, to your configuration like this:

```yaml
version: 1
```

This is not mandatory. If the version is not given, the configuration may
not work in future versions of freezeyt.


### Application to freeze  {: #conf-app }

The name of importable Python module that contains the application must be
given in the configuration, or on the command line as first argument.

Inside the module, *freezeyt* looks for the variable *app* by default.
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

To output the frozen website to a directory, specify
the directory name as a string:

```yaml
output: ./_build/
```

If output is not specified in the configuration,
you must specify it on the command line, either by the `--output` (`-o`)
option or as a second positional argument.

---
<!-- continue from here -->

The output must be specified just by one way otherwise is an error.

If there is any existing content in the output directory,
freezeyt will either remove it (if the content looks like a previously
frozen website) or raise an error.
Best practice is to remove the output directory before freezing.

#### The full form

Or use the full form – using the `dir` *saver*:

```yaml
output:
    type: dir
    dir: ./_build/
```

#### Output to dictionary

For testing, `freezeyt` can output to a dictionary rather than save
files to the disk.
This can be configured with:

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

This is not useful in the CLI, as the return value is lost.


### URL prefix  {: #conf-prefix }

The URL where the application will be deployed can be
specified with:

```yaml
prefix: http://localhost:8000/
```
or
```yaml
prefix: https://mysite.example.com/subpage/
```

Freezeyt will freeze all pages starting with `prefix` that
it finds.

The prefix can also be specified on thecommand line with e.g.:
`--prefix=http://localhost:8000/`.
The CLI argument has priority over the config file.


## Extra content


### Extra pages  {: #conf-extra_pages }

URLs of pages that are not reachable by following links from the homepage
can specified as “extra” pages in the configuration:

```yaml
extra_pages:
    - /extra/
    - /extra2.html
```

Freezeyt will handle these pages as if it found them by following links.
(For example, by default it will follow links in extra pages.)

Extra pages may also be given on the command line,
e.g. `--extra-page /extra/ --extra-page /extra2.html`.
The lists from CLI and the config file are merged together.

You can also specify extra pages using a Python generator,
specified using a module name and function name as follows:

```yaml
extra_pages:
    - generator: my_app:generate_extra_pages
```

The `generate_extra_pages` function should take the application
as argument and return an iterable of URLs.

When using the Python API, a generator for extra pages can be specified
directly as a Python object, for example:

```python
config = {
   ...
   'extra_pages': [{'generator': my_generator_function}],
}
another_config = {
   ...
   'extra_pages': [my_generator_function],
}
```

### Extra files  {: #config-extra_files }

Extra files to be included in the output can be specified,
along with their content.

These files are not considered part of the app; freezeyt will not try to find
links in them.

This is useful for configuration of your static server.
(For pages that are part of your website, we recommend
adding them to your application rather than as extra files.)

If you specify backslashes in `url part`, `freezeyt` convert them to forward slashes.

For example, the following config will add 3 files to
the output:

```yaml
extra_files:
      CNAME: mysite.example.com
      ".nojekyll": ''
      config/xyz: abc
```

You can also specify extra files using Base64 encoding or
a file path, like so:


```yaml
extra_files:
    config.dat:
        base64: "YWJjZAASNA=="
    config2.dat:
        copy_from: included/config2.dat
```

It's possible to recursively copy an entire directory using `copy_from`,
as in:


```yaml
extra_files:
    static:
        copy_from: static/
```

Extra files cannot be specified on the CLI.


## Debugging options


### Clean up  {: #conf-cleanup }

If an error occurs during the "freeze" process, Freezeyt will delete the incomplete output directory.
This prevents, for example, uploading incomplete results to a web hosting by mistake.

If you want to keep the incomplete directory (for example,
to help debugging), you can use the `--no-cleanup` switch
or the `cleanup` key in the configuration file:

```yaml
cleanup: False
```

The command line switch has priority over the configuration.
Use `--no-cleanup` to override `cleanup: False` from the config.


### Fail fast  {: #conf-fail_fast }

Fail fast mode stops the freezing of the app when the first error occurs.

As with most settings, fail fast can be set both in the configuration file and in the command line using switches (the command line always overrides the configuration file).
The fail fast is defined as `boolean` option.

If you want to specified fail fast in configuration file, use key `fail_fast` with
 `boolean` values `True` or `False`:

```yaml
fail_fast: True
```

If you want to specified fail fast from command line, use switches
 `--fail-fast` (short `-x`) resp. `--no-fail-fast` to disable it:

```shell
$ freezeyt app -o output -x
```


## Built-in plugins


### Github Pages Plugin  {: #conf-gh_pages }

To make it easier to upload frozen pages to ([Github Pages service](https://pages.github.com/)), you can also use the `--gh-pages` switch or the `gh_pages` key  in the configuration file, which creates a gh-pages git branch in the output directory.

By default, the Github Pages Plugin is not active, however, if you have activated this plugin in your configuration, you can always override the current configuration with `--no-gh-pages` switch in the CLI.

Configuration example:
```yaml
gh_pages: True
```

To deploy a site to Github, you can then work with the git repository directly in the output directory or pull the files into another repository/directory.
You can then pull/fetch files from the newly created gh-pages git branch in many ways, e.g:
```shell
git fetch output_dir gh-pages
git branch --force gh-pages FETCH_HEAD
```
Note: This will overwrite the current contents of the `gh-pages` branch, because of the `--force` switch.


### Progress bar and logging  {: #conf-cli-progress }

The CLI option `--progress` controls what `freezeyt` outputs as it
handles pages:

* `--progress=log`: Output a message about each frozen page to stdout.
* `--progress=bar`: Draw a status bar in the terminal. Messages about
  each frozen page are *also* printed to stdout.
* `--progress=none`: Don't do any of this.

The default is `bar` if stdout is a terminal, and `log` otherwise.

It is possible to configure this in the config file using the plugins
`freezeyt.progressbar:ProgressBarPlugin` and `freezeyt.progressbar:LogPlugin`.
See below on how to enable plugins.


## Freezing


### Comparison of MIME type and file type

Freezeyt checks whether the file extensions in its output
correspond to the MIME types served by the app.
If there's a mismatch, freezeyt fails, because this means a server
wouldn't be able to serve the page correctly.

This funtionality is provided by `freezeyt.Middleware`.

#### Default MIME type  {: #conf-default_mimetype }

It is possible to specify the MIME type used for files without an extension.
For example, if your server of static pages defaults to plain text files,
use:

```yaml
default_mimetype=text/plain
```

If the default MIME type isn't explicitly configured in YAML configuration,
then the `freezeyt` uses value `application/octet-stream`.

The default mimetype cannot be specified on the CLI.

#### MIME type getter  {: #conf-get_mimetype }

There is possibility to modify the way how to determine file type
from file extension.
You can setup your own `get_mimetype` function.

Freezeyt will register your own function, if you specify it in configuration
YAML file as:

```yaml
get_mimetype=module:your_function
```

If the `get_mimetype` is not defined in configuration file,
then `freezeyt` calls the python function `mimetypes.guess_type`
and uses the mimetype (the first element) it returns.

`get_mimetype` can be defined as:
* strings in the form `"module:function"`, which name the function to call,
* Python functions (if configuring `freezeyt` from Python, e.g. as a `dict`,
  rather than YAML).

The `get_mimetype`:
* gets one argument - the `filepath` as `str`

* returns file MIME types as a `list` of MIME types
  (e.g. `["text/html"]` or `["audio/wav", "audio/wave"]`).

If `get_mimetype` returns `None`, `freezeyt` will use the configured `default_mimetype`
(see *Default MIME type* above).

The get_mimetype function cannot be specified on the CLI.


#### Using a mime-db database  {: #conf-mime_db_file }

There is an option to use [the MIME type database from the `jshttp` project](https://github.com/jshttp/mime-db/blob/master/db.json),
or a database with the same structure.
(This is the database used by GitHub Pages).
The database will be used to get file MIME type from file suffix.

To use this database, add the path to the JSON file to `freezeyt` configuration:
```yaml
mime_db_file=path/to/mime-db.json
```
This is equivalent to setting `get_mimetype` to a function that maps
extensions to filetypes according to the database.

The mime_db file cannot be specified on the CLI.

### URL finding  {: #conf-url_finders }

`freezeyt` discovers new links in the application by URL finders. URL finders
are functions whose goal is to find url of specific MIME type.
`freezeyt` offers different configuration options to use URL finders:

* use predefined URL finders for `text/html` or `text/css` (default),
* define your own URL finder as your function,
* turn off some of finders (section below)

Example of configuration:

```yaml
url_finders:
    text/html: get_html_links
    text/css: get_css_links
```

Keys in the `url_finders` dict are MIME types;

Values are URL finders, which can be defined as:
* strings in the form `"module:function"`, which name the finder
  function to call,
* strings like `get_html_links`, which name a function from the
  `freezeyt.url_finders` module, or
* Python functions (if configuring `freezeyt` from Python rather than
  YAML).


An URL finder gets these arguments:
* page content `BinaryIO`,
* the absolute URL of the page, as a `string`,
* the HTTP headers, as a list of tuples (WSGI).

The function should return an iterator of all URLs (as strings) found
in the page's contents, as they would appear in `href` or `src` attributes.
Specifically:

- The URLs can be relative.
- External URLs (i.e. those not beginning with `prefix`) should be included.

Finder functions may be asynchronous:
- The function can be defined with `async def` (i.e. return a
  coroutine). If it is, freezeyt will use the result after `await`.
- The function may be an asynchronous generator (defined with `async def`
  and use `yield`). If so, freezeyt will use async iteration to handle it.

The `freezeyt.url_finders` module includes:
- `get_html_links`, the default finder for HTML
- `get_css_links`, the default finder for CSS
- `get_html_links_async` and `get_css_links_async`, asynchronous variants
  of the above
- `none`, a finder that doesn't find any links.

URL finders cannot be specified in the CLI.

#### URL finder header

You can specify a finder in the `Freezeyt-URL-Finder` HTTP header.
If given, it overrides the `url_finders` configuration.

#### Default `get_html_links`

The default URL finder for HTML pages looks in `src` and `href` attributes
of all tags in the document.
It currently does not handle other links, such as embedded CSS, but it
may be improved in the future.

#### Default `get_css_links`

The default URL finder for CSS uses the [`cssutils`](https://pypi.org/project/cssutils/) library to find all
links in a stylesheet.

#### Disabling default URL finders  {: #conf-use_default_url_finders }

If a finder is not explictly specified in the configuration file, `freezeyt` will use the
default for certain MIME type. For example, if you specify
`text/html: my_custom_finder` only, `freezeyt` will use the default finder
for `text/css`.

You can disable this behaviour:

```yaml
use_default_url_finders: false
```


#### Finding URLs in Link headers  {: #conf-urls_from_link_headers }

By default, `freezeyt` will follow URLs in `Link` HTTP headers.
To disable this, specify:

```yaml
urls_from_link_headers: false
```


### Freeze actions

By default, `freezeyt` will save the pages it finds.
You can instruct it to instead ignore certain pages, or treat them as errors.
This is most useful as a response to certain HTTP statuses (e.g. treat all
`404 NOT FOUND` pages as errors), but can be used independently.

To tell `freezeyt` what to do from within the application (or middleware),
set the `Freezeyt-Action` HTTP header to one of these values:

* `'save'`: `freezeyt` will save the body of the page.
* `'ignore'`: `freezeyt` will not save any content for the page
* `'warn'`: will save the content and send warn message to stdout
* `'follow'`: `freezeyt` will save content from the redirected location
  (this requires a `Location` header, which is usually added for redirects).
  Redirects to external pages are not supported.
* `'error'`: fail; the page will not be saved and `freeze()` will raise
  an exception.


#### HTTP Status handling  {: #conf-status_handlers }

If the `Freezeyt-Action` header is not set, `freezeyt` will determine what to
do based on the status.
By default, `200 OK` pages are saved and any others cause errors.
The behavior can be customized using the `status_handlers` setting.
For example, to ignore pages with the `404 NOT FOUND` status, set the
`404` handler to `'ignore'`:

```yaml
status_handlers:
    '404': ignore
```

For example, `status_handlers` would be specified as:

```yaml
status_handlers:
    '202': warn
    '301': follow
    '404': ignore
    '418': my_module:custom_action  # see below
    '429': ignore
    '5xx': error
```

Note that the status code must be a string, so it needs to be quoted in the YAML file.

A range of statuses can be specified as a number (`1-5`) followed by lowercase `xx`.
(Other "wildcards" like `50x` are not supported.)

Status handlers cannot be specified in the CLI.

#### Custom actions

You can also define a custom action in `status_handlers` as:
* a string in the form `'my_module:custom_action'`, which names a handler
  function to call,
* a Python function (if configuring `freezeyt` from Python rather than from
  YAML).

The action function takes one argument, `task` (TaskInfo): information about the freezing task.
See the `TaskInfo` hook for a description.
Freezeyt's default actions, like `follow`, can be imported from `freezeyt.actions`
(e.g. `freezeyt.actions.follow`).
A custom action should call one of these default actions and return the return value from it.


### Path generation

It is possible to customize the filenames that URLs are saved under
using the `url_to_path` configuration key, for example:

```yaml
url_to_path: my_module:url_to_path
```

The value can be:
* a strings in the form `"module:function"`, which names the
  function to call (the function can be omitted along with the colon,
  and defaults to `url_to_path`), or
* a Python function (if configuring `freezeyt` from Python rather than
  YAML).

The function receives the *path* of the URL to save, relative to the `prefix`,
and should return a path to the saved file, relative to the build directory.

The default function, available as `freezeyt.url_to_path`, adds `index.html`
if the URL path ends with `/`.

`url_to_path` cannot be specified in the CLI.

### Plugins  {: #conf-plugins }

It is possible to extend `freezeyt` with *plugins*, either ones that
ship with `freezeyt` or external ones.

Plugins are added using configuration like:

```yaml
plugins:
    - freezeyt.progressbar:ProgressBar
    - mymodule:my_plugin
```


### Middleware static mode  {: #static_mode }

When using the `freezeyt` middleware, you can enable *static mode*,
which simulates behaviour after the app is saved to static pages:

```yaml
static_mode: true
```

Currently in static mode:
- HTTP methods other than GET and HEAD are disallowed.
- URL parameters are removed
- The request body is discarded

Other restrictions and features may be added in the future, without regard
to backwards compatibility.
The static mode is intended for interactive use -- testing your app without
having to freeze all of it after each change.



## Extending *freezeyt*


### Custom plugins

A plugin is a function that `freezeyt` will call before starting to
freeze pages.

It is passed a `FreezeInfo` object as argument (see the `start` hook below).
Usually, the plugin will call `freeze_info.add_hook` to register additional
functions.


### Hooks  {: #conf-hooks }

It is possible to register *hooks*, functions that are called when
specific events happen in the freezing process.

For example, if `mymodule` defines functions `start` and `page_frozen`,
you can make freezeyt call them using this configuration:

```yaml
hooks:
    start:
        - mymodule:start
    page_frozen:
        - mymodule:page_frozen
```

When using the Python API, a function can be used instead of a name
like `mymodule:start`.

#### `start`

The function will be called when the freezing process starts,
before any other hooks.

It is passed a `FreezeInfo` object as argument.
The object has the following attributes:

* `add_url(url, reason=None)`: Add the URL to the set of pages to be frozen.
  If that URL was frozen already, or is outside the `prefix`, does nothing.
  If you add a `reason` string, it will be used in error messages as the reason
  why the added URL is being handled.
* `add_hook(hook_name, callable)`: Register an additional hook function.
* `total_task_count`: The number of pages `freezeyt` currently “knows about” –
  ones that are already frozen plus ones that are scheduled to be frozen.
* `done_task_count`: The number of pages that are done (either successfully
  frozen, or failed).
* `failed_task_count`: The number of pages that failed to freeze.

#### `page_frozen`

The function will be called whenever a page is processed successfully.
It is passed a `TaskInfo` object as argument.
The object has the following attributes:

* `get_a_url()`: returns a URL of the page, including `prefix`.
  Note that a page may be reachable via several URLs; this function returns
  an arbitrary one.
* `path`: the relative path the content is saved to.
* `freeze_info`: a `FreezeInfo` object. See the `start` hook for details.
* `exception`: for failed tasks, the exception raised;
  `None` otherwise.
* `reasons`: A list of strings explaining why the given page was visited.
  (Note that as the freezing progresses, new reasons may be added to
  existing tasks.)


#### `page_failed`

The function will be called whenever a page is not saved due to an
exception.
It is passed a `TaskInfo` object as argument (see the `page_frozen` hook).


#### `success`

The function will be called after the app is successfully frozen.
It is passed a `FreezeInfo` object as argument (see the `start` hook).
