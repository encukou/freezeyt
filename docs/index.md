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
You can use [`venv`], `virtualenv`, Conda, containers or any other kind
of virtual environment.

[`venv`]: https://docs.python.org/3/library/venv.html?highlight=venv#module-venv

The tool can be installed using:

```console
$ python -m pip install .
```


## Usage

To use freezeyt, you need a Python web application.
You can use the [example Flask app].

[example Flask app]: https://flask.palletsprojects.com/en/1.1.x/quickstart/

Both the application and Freezeyt must be importable (installed)
in your environment.

Run freezeyt with the name of your application and the
output directory. For example:

```console
$ python -m freezeyt my_app _build
```

The output directory (here, `_build`), should either not exist yet
or contain output from a previous run of Freezeyt.
Any existing files in it will be removed.


## More examples of CLI usage

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

From asynchronous code running in an `asyncio` event loop,
you can call `freeze_async` instead of `freeze`.


### Middleware

Some of Freezeyt's functionality is available as a WSGI middleware.
To use it, wrap your application in `freezeyt.Middeleware`. For example:

```python
from freezeyt import Middleware

config = {'prefix': 'https://pyladies.cz/'}

app = Middleware(app, config)
```


[Configuration]: config.md

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
