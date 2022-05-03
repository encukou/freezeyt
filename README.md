# freezeyt

Static web page generator created by the Czech Python community.


## What this does

Freezeyt is a static webpage *freezer*.
It takes a Python web application and turns it into a set of files
that can be served by a simple server like [GitHub Pages] or
Python's [http.server].

[GitHub Pages]: https://docs.github.com/en/free-pro-team@latest/github/working-with-github-pages/about-github-pages
[http.server]: https://docs.python.org/3/library/http.server.html

Freezeyt is compatible with all Python web frameworks that use the common
[Web Server Gatweay Interface] (WSGI)

[Web Server Gatweay Interface]: https://www.python.org/dev/peps/pep-3333/


## Installation

Freezeyt requires Python 3.6 or above.

It is highly recommended to create and activate a separate virtual
environment for this project.
You can use [`venv`], `virtualenv`, Conda, containers or any other kind
of virtual environment.

[`venv`]: https://docs.python.org/3/library/venv.html?highlight=venv#module-venv

The tool can be installed using:

```
$ python -m pip install .
```


## Usage

To use freezeyt, you need a Python web application.
You can use the [example Flask app].

[example Flask app]: https://flask.palletsprojects.com/en/1.1.x/quickstart/

Your WSGI application should be named `app`.
Both the application and Freezeyt must be importable (installed)
in your environment.

Run freezeyt with the name of your application and the
output directory. For example:

```shell
$ python -m freezeyt my_app _build
```

Freezeyt may overwrite the build directory (here, `_build`),
removing all existing files from it.

For more options, see Configuration below.


### Python API

Freezeyt also has a Python API, the `freeze` function
that takes an application to freeze and a configuration dict:

```python
from freezeyt import freeze
freeze(app, config)
```

The `config` should be a dict as if read from a YAML configuration
file (see Configuration below).

From asynchronous code running in an `asyncio` event loop,
you can call `freeze_async` instead of `freeze`.


## Configuration

While common options can be given on the command line,
you can have full control over the freezing process with a YAML
configuration file or a variable with the configuration.
You can specify a config file using the `-c/--config` option,
for example:

```shell
$ python -m freezeyt my_app _build -c freezeyt.yaml
```

The configuration variable should be a dictionary.
To pass the config variable, use the `-C/--import-config` option,
for example:

```shell
$ python -m freezeyt my_app _build -C my_app:freezeyt_config
```

Here is an example configuration file:

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
    CNAME: https://mysite.example.com/
    ".nojekyll": ''
    googlecc704f0f191eda8f.html:
        copy_from: google-verification.html
status_handlers:
    # If a redirect page (HTTP status 3xx) is found, warn but don't fail
    "3xx": warn
```

The following options are configurable:

### Module Name

The module that contains the application must be given on the
command line.
In it, Freezyt looks for the variable `app`.
A different variable can be specified using `:`.

Examples:

    application
or

    folder1.folder2.application
or

    my_app:wsgi_application


### Output

To outupt the frozen website to a directory, specify
the directory name:

```yaml
output: ./_build/
```

Or use the full form – using the `dir` *saver*:

```yaml
output:
    type: dir
    dir: ./_build/
```

If output is not specified in the configuration file,
you must specify the oputput directory on the command line.
Specifying it both on the command line and in the config file
is an error.

If there is any existing content in the output directory,
freezeyt will either remove it (if the content looks like a previously
frozen website) or raise an error.
Best practice is to remove the output directory before freezing.



#### Output to dict

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


### Prefix

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


### Extra pages

URLs of pages that are not reachable by following links from the homepage
can specified as “extra” pages in the configuration:

```yaml
extra_pages:
    - /extra/
    - /extra2.html
```

Freezeyt will freeze these pages in addition to those it
finds by following links.

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


### Extra files

Extra files to be included in the output can be specified,
along with their content.

This is useful for configuration of your static server.
(For pages that are part of your website, we recommend
adding them to your application rather than as extra files.)

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


### Clean up

If an error occurs during the "freeze" process, Freezeyt will delete the incomplete output directory.
This prevents, for example, uploading incomplete results to a web hosting by mistake.

If you want to keep the incomplete directory (for example,
to help debugging), you can use the `--no-cleanup` switch
or the `cleanup` key  in the configuration file:

```yaml
cleanup: False
```

The command line switch has priority over the configuration.
Use `--no-cleanup` to override `cleanup: False` from the config.


### Comparison of MIME type and file type

Freezeyt checks whether the file extensions in its output
correspond to the MIME types served by the app.
If there's a mismatch, freezeyt fails, because this means a server
wouldn't be able to serve the page correctly.

#### Default MIME type

It is possible to specify the MIME type used for files without an extension.
For example, if your server of static pages defaults to plain text files,
use:

```yaml
default_mimetype=text/plain
```

If the default MIME type isn't explicitly configured in YAML configuration,
then the `freezeyt` uses value `application/octet-stream`.

The default mimetype cannot be specified on the CLI.

#### Recognizing file types from extensions

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


#### Using a mime-db database

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


### Progress bar and logging

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

### Configuration version

To ensure that your configuration will work unchanged in newer versions of freezeyt,
you should add the current version number, `1`, to your configuration like this:

```yaml
version: 1
```

This is not mandatory. If the version is not given, the configuration may
not work in future versions of freezeyt.

The version parameter is not accepted on the command line.

### Plugins

It is possible to extend `freezeyt` with *plugins*, either ones that
ship with `freezeyt` or external ones.

Plugins are added using configuration like:

```yaml
plugins:
    - freezeyt.progressbar:ProgressBar
    - mymodule:my_plugin
```

#### Custom plugins

A plugin is a function that `freezeyt` will call before starting to
freeze pages.

It is passed a `FreezeInfo` object as argument (see the `start` hook below).
Usually, the plugin will call `freeze_info.add_hook` to register additional
functions.


### Hooks

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


### Status handling

The `status_handlers` option defines the way to handle HTTP statuses.
For example, the default reaction to a `404 NOT FOUND` status is to quit with an error,
but you can customize `freezeyt` to ignore the default error.

```yaml
status_handlers:
    '404': ignore
```

`freezeyt` includes a few pre-defined handlers:
* `'warn'`: will save the content and send warn message to stdout
* `'save'`: `freezeyt` will save the body of the page.
  This is the default for status `200 OK`.
* `'follow'`: `freezeyt` will save content from the redirected location
  (this requires a `Location` header, which is usually added for redirects – `3xx` statuses).
  Redirects to external pages are not supported.
* `'ignore'`: `freezeyt` will not save any content for the page
* `'error'`: fail; the page will not be saved and `freeze()` will raise
  an exception.

The user can also define a custom handler as:
* a string in the form `'my_module:custom_handler'`, which names a handler
  function to call,
* a Python function (if configuring `freezeyt` from Python rather than from
  YAML).

The handler function takes one argument, `task` (TaskInfo): information about the freezing task.
See the `TaskInfo` hook for a description.
A custom handler should call one of the pre-defined handlers (e.g. `freezeyt.status_handlers.follow`) and return the return value from it.

Freezeyt's default functions, like `follow`, can be imported from `freezeyt.status_handlers` and used
from the custom handlers.

For example, `status_handlers` would be specified as:

```yaml
status_handlers:
    '202': warn
    '301': follow
    '404': ignore
    '418': my_module:custom_handler
    '429': ignore
    '5xx': error
```

Note that the status code must be a string, so it needs to be quoted in the YAML file.

A range of statuses can be specified as a number (`1-5`) followed by lowercase `xx`.
(Other "wildcards" like `50x` are not supported.)

Status handlers cannot be specified in the CLI.


### URL finding

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

The `freezeyt.url_finders` module includes the default finders `get_html_links`
and `get_css_links`, and their asynchronous variants `get_html_links_async`
and `get_css_links_async`.

URL finders cannot be specified in the CLI.

#### Default `get_html_links`

The default URL finder for HTML pages looks in `src` and `href` attributes
of all tags in the document.
It currently does not handle other links, such as embedded CSS, but it
may be improved in the future.

#### Default `get_css_links`

The default URL finder for CSS uses the `css_parser` library to find all
links in a stylesheet.

#### Disabling default URL finders

If a finder is not explictly specified in the configuration file, `freezeyt` will use the
default for certain MIME type. For example, if you specify
`text/html: my_custom_finder` only, `freezeyt` will use the default finder
for `text/css`.

You can disable this behaviour:

```yaml
use_default_url_finders: false
```

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


## Examples of CLI usage

```shell
$ python -m freezeyt my_app _build/
```

```shell
$ python -m freezeyt my_app _build/ --prefix https://pyladies.cz/
```

```shell
$ python -m freezeyt my_app _build/ -c config.yaml
```

```shell
$ python -m freezeyt my_app _build/ --prefix https://pyladies.cz/ --extra-page /extra1/ --extra-page /extra2/
```

```shell
$ python -m freezeyt my_app _build/ --prefix https://pyladies.cz/ --extra-page /extra1/ --extra-page /extra2/ --config path/to/config.yaml
```


## Contributing

Are you interested in this project? Awesome!
Anyone who wants to be part of this project and who's willing
to help us is very welcome.
Just started with Python? Good news!
We're trying to target mainly the beginner Pythonistas who
are seeking opportunities to contribute to (ideally open source)
projects and who would like to be part of an open source community
which could give them a head start in their
(hopefully open source :)) programming careers.

Soo, what if you already have some solid Python-fu?
First, there's always something new to learn, and second,
we'd appreciate if you could guide the “rookies” and pass on
some of the knowledge onto them.

Contributions, issues and feature requests are welcome.
Feel free to check out the [issues] page if you'd like to
contribute.

[issues]: https://github.com/encukou/freezeyt/issues


## How to contribute

1. Clone this repository to your local computer:

```shell
$ git clone https://github.com/encukou/freezeyt
```

2. Then fork this repo to your GitHub account
3. Add your forked repo as a new remote to your local computer:

```shell
$ git remote add <remote_label> https://github.com/<username>/freezeyt
```

4. Create a new branch at your local computer

```shell
$ git branch <branch_name>
```

5. Switch to your new branch

```shell
$ git switch <branch_name>
```

6. Update the code
7. Push the changes to your forked repo on GitHub

```shell
$ git push <remote_label> <branch_name>
```

8. Finally, make a pull request from your GitHub account to origin


### Installing for development

`freezeyt` can be installed from the current directory:

```shell
$ python -m pip install -e .
```

It also has several groups of extra dependecies:
* `blog` for the project blog
* `dev` for development and running tests
* `typecheck` for mypy type checks

Each group can be installed separately:

```shell
$ python -m pip install -e ."[typecheck]"
```

or you can install more groups at once:
```shell
$ python -m pip install -e ."[blog, dev, typecheck]"
```


### Using an in-development copy of freezeyt

* Set `PYTHONPATH` to the directory with `freezeyt`, for example:
  * Unix: `export PYTHONPATH="/home/name/freezeyt"`
  * Windows: `set PYTHONPATH=C:\Users\Name\freezeyt`

* Install the web application you want to freeze. Either:
  * install the application using `pip`, if possible, or
  * install the application's dependencies and `cd` to the app's directory.

* Run freezeyt, for example:
  * `python -m freezeyt demo_app_url_for _build --prefix http://freezeyt.test/foo/`



### Tests

For testing the project it's necessary to install additional requirements:

```
$ python -m pip install .[dev]
```

To run tests in your current environment, use pytest:

```
$ python -m pytest
```

To run tests with multiple Python versions (if you have them installed),
install `tox` using `python -m pip install tox` and run it:

```
$ tox
```

#### Environ variables for tests

Some test scenarios compare freezeyt's results with expected output.
When the files with expected output don't exist yet,
they can be created by setting the environment variable
`TEST_CREATE_EXPECTED_OUTPUT` to `1`:

**Unix**

```shell
$ export TEST_CREATE_EXPECTED_OUTPUT=1
```

**Windows**

```shell
> set TEST_CREATE_EXPECTED_OUTPUT=1
```

If you set the variable to any different value or leave it unset
then the files will not be recreated
(tests will fail if the files are not up to date).

When output changes, you need to first delete the expected output,
regenerate it by running tests with `TEST_CREATE_EXPECTED_OUTPUT=1`,
and check that the difference is correct.

### Tools and technologies used

* [PEP 3333 - Python WSGI](https://www.python.org/dev/peps/pep-3333/)
* [flask](https://flask.palletsprojects.com/en/1.1.x/)
* [pytest](https://docs.pytest.org/en/latest/)
* [html5lib](https://html5lib.readthedocs.io/en/latest/)


### How to watch progress
Unfortunately our progress of development can be watched only in Czech language.

Watch the progress:

* [Youtube playlist](https://www.youtube.com/playlist?list=PLFt-PM7J_H3EU5Oez3ZSVjY5pZJttP2lT)

Other communication channels and info can be found here:
* [Google doc in Czech](https://tinyurl.com/freezeyt)


### Freezeyt Blog

We keep a blog about the development of Freezeyt.
It is available [here](https://encukou.github.io/freezeyt/).

**Be warned:** some of it is in the Czech language.

#### Blog development

The blog was tested on Python version 3.8.

The blog is a Flask application.
To run it, install additional dependecies with
`python -m pip install .[blog]`.
Then, set the environment variable `FLASK_APP` to the path of the
blog app.
Also set `FLASK_ENV` to "development" for easier debugging.
Then, run the Flask server.

1. On Microsoft Windows:

```shell
> python -m pip install .[blog]
> set FLASK_APP=freezeyt_blog/app.py
> set FLASK_ENV=development
> flask run
```

2. On UNIX:

```shell
$ python -m pip install .[blog]
$ export FLASK_APP=freezeyt_blog/app.py
$ export FLASK_ENV=development
$ flask run
```

The URL where your blog is running will be printed on the terminal.

Once you're satisfied with how the blog looks, you can freeze it with:

```shell
$ python -m freezeyt freezeyt_blog.app freezeyt_blog/build
```

#### Adding new articles to freezeyt blog

Articles are writen in the `Markdown` language.

**Article** - save to directory `../freezeyt/freezeyt_blog/articles`

**Images to articles** - save to directory `../freezeyt/freezeyt_blog/static/images`

If te files are saved elsewhere, the blog will not work correctly.


## History

### Why did the project start?

The Czech Python community uses a lot of static web pages that
are generated from a web application for community purposes.
For example, organizing and announcing workshops, courses,
or meetups.

The community has been so far relying on [Frozen Flask] and [elsa]
in order to generate the static web content.
The new [freezer] ought to be used with any arbitrary Python Web
application framework ([Flask], [Django], [Tornado], etc.).
So the community won't be limited by one web app technology for
generating static pages anymore.

[Frozen Flask]: https://pythonhosted.org/Frozen-Flask/
[elsa]: https://github.com/pyvec/elsa/
[freezer]: https://github.com/encukou/freezeyt
[Flask]: https://flask.palletsprojects.com/en/1.1.x/
[Django]: https://www.djangoproject.com/
[Tornado]: https://www.tornadoweb.org/en/stable/


## Authors
See GitHub history for all [contributors](https://github.com/encukou/freezeyt/graphs/contributors).


## License

This project is licensed under the [MIT License](LICENCE.MIT).
May it serve you well.
