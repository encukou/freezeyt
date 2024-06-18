---
title: freezeyt
...

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
[Web Server Gateway Interface] (WSGI)

[Web Server Gateway Interface]: https://www.python.org/dev/peps/pep-3333/


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


### Middleware

Some of Freezeyt's functionality is available as a WSGI middleware.
To use it, wrap your application in `freezeyt.Middeleware`. For example:

```python
from freezeyt import Middleware

config = {}  # use a configuration dict as for `freeze(app, config)`

app = Middleware(app, config)
```


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
