---
title: freezeyt
...

# freezeyt

Freezeyt turns Python web applications into static websites.


## What this does

Freezeyt is a static webpage *freezer*.
It takes a Python web application and turns it into a set of files
that can be served by a simple server like [GitHub Pages] or
Python's [http.server].

[GitHub Pages]: https://docs.github.com/en/free-pro-team@latest/github/working-with-github-pages/about-github-pages
[http.server]: https://docs.python.org/3/library/http.server.html

Freezeyt is compatible with all Python web frameworks that use the common
[Web Server Gateway Interface] (WSGI).

[Web Server Gateway Interface]: https://www.python.org/dev/peps/pep-3333/


## Installation

Freezeyt requires Python 3.6 or above.

It is highly recommended to create and activate a separate virtual
environment for this project.
You can use [`venv`][venv], `virtualenv`, Conda, containers or any other kind
of virtual environment.

[venv]: https://docs.python.org/3/library/venv.html?highlight=venv#module-venv

The tool can be installed using:

```console
$ python -m pip install freezeyt
```

To install a development version of Freezeyt,
see [Contributing documentation].

[Contributing documentation]: ./contrib.md


## Quick usage

For a Flask app in `hello.py`, run:

```console
$ python -m freezeyt hello _build
```

For detailed instructions, read on.


## Usage

To use Freezeyt, you need a Python web application.
You can use the [example Flask app] to start.

[example Flask app]: https://flask.palletsprojects.com/en/2.3.x/quickstart/

Specifically, Freezeyt needs a WSGI application,
ideally one named `app` which is the default in [Flask] and [Falcon].
For other frameworks, search the documentation on how to export a WSGI
application.

Both the application and Freezeyt need to be importable (installed) in your
envuronment.

Run Freezeyt with two arguments: the Python module with your `app`,
and an output directory.
Note that Freezeyt wants a *module* name (as used in an `import` statement).
Don't use a *file* name with a `.py` suffix.

For example, if your `app` is defined in the file `my_app.py`, run:

```console
$ python -m freezeyt my_app _build
```

If your application is not named `app`, give its name after a colon.
For example, a [Django WSGI application] is usually in
the `wsgi` submodule and named `application`, so you should run:

```console
$ python -m freezeyt my_project.wsgi:application _build
```

The output directory (here, `_build`), should either not exist yet
or contain output from a previous run of Freezeyt.
Any existing files in it will be removed.
(Freezeyt tries to avoid deleting data it didn't create itself,
but do not rely on this.)

[WSGI application]: https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/


### More examples of CLI usage

You can tell Freezeyt where the application will be hosted,
so it can generate correct URLs:

```console
$ python -m freezeyt my_app _build/ --prefix https://pyladies.cz/
```

You can save options like the *prefix* in a file (see [Configuration]),
and then use the `--config` (`-c`) option to use the file:

```console
$ python -m freezeyt my_app _build/ --config config.yaml
```

If you use both a configuration file and  CLI options like `--prefix`,
the options override settings from the file:

```console
$ python -m freezeyt my_app _build/ --prefix https://pyladies.cz/ --config path/to/config.yaml
```


### Python API

Freezeyt also has a Python API: the `freeze` function
that takes an application to freeze and a configuration dict.
For example:

```python
from freezeyt import freeze

config = {'prefix': 'https://pyladies.cz/'}

freeze(app, config)
```

The `config` should be a dict as if read from a YAML configuration
file (see [Configuration]).

From asynchronous code running in an [`asyncio`][asyncio] event loop,
you can call `freeze_async` instead of `freeze`.

[asyncio]: https://docs.python.org/3/library/asyncio.html


### Middleware  {: #middleware }

Some of Freezeyt's functionality is available as a WSGI middleware.
To use it, wrap your application in `freezeyt.Middeleware`. For example:

```python
from freezeyt import Middleware

config = {'prefix': 'https://pyladies.cz/'}

app = Middleware(app, config)
```


[Configuration]: config.md

## Project info

### History

The Czech Python community uses a lot of static web pages that
are generated from a web application for community purposes.
For example, organizing and announcing workshops, courses,
or meetups.

The community has been so far relying on [Frozen Flask] and [elsa]
in order to generate the static web content.
The new freezer ought to be used with any arbitrary Python Web
application framework ([Flask], [Django], [Falcon], [Tornado], etc.).
So the community won't be limited by one technology anymore.

[Frozen Flask]: https://frozen-flask.readthedocs.io/en/latest/
[elsa]: https://github.com/pyvec/elsa/
[freezer]: https://github.com/encukou/freezeyt
[Django]: https://www.djangoproject.com/
[Tornado]: https://www.tornadoweb.org/en/stable/
[Flask]: https://flask.palletsprojects.com/en/3.0.x/
[Falcon]: https://falconframework.org/


### Authors
See GitHub history for all [contributors](https://github.com/encukou/freezeyt/graphs/contributors).


### License

This project is licensed under an [MIT License](licence.md).
May it serve you well.
