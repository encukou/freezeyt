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

The needed requirements can be installed using:

```
$ python -m pip install -r requirements.txt
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


## Configuration

While common options can be given on the command line,
you can full control over the freezing process with a YAML
configuration file.
You can specify a config wile using the `-c/--config` option,
for example:

```shell
$ python -m freezeyt my_app _build -c freezeyt.yaml
```

The following options are configurable:

### Module Name

The module that contains the application must be given on the 
command line.
In it, Freezyt looks for the variable `app`.

Examples:

    application
or

    folder1.folder2.application


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

For testing, Freezeyt can also output to a dictionary.
This can be configured with:

```yaml
output:
    type: dict
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

A list of URLs to “extra” pages within the application can
be given using:
```yaml
extra_pages:
    - /extra/
    - /extra2.html
```

Freezeyt will freeze these pages in addition to those it
finds by following links.

Extra pages may also be give on the command line,
e.g. `--extra-page /extra/ --extra-page /extra2.html`.
The lists from CLI and the config file are merged together.


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

Extra files cannot be specified on the CLI.

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
$ git remote add <name_your_remote> https://github.com/<your_username>/freezeyt
```

4. Create new branch at your local computer

```shell
$ git branch <name_new_branch>
```

5. Switch to your new branch

```shell
$ git switch <name_new_branch>
```

6. Make some awesome changes in code
7. Push changes to your forked repo on GitHub

```shell
$ git push <your_remote> <your_new_branch>
```

8. Finally make a pull request from your GitHub account to origin

9. Repeat this process until we will have done amazing freezer


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
$ python -m pip install -r requirements-dev.txt
```

To run tests in your current environment, use pytest:

```
$ python -m pytest
```

To run tests with multiple Python versions (if you have them installed),
install `tox` using `python -m pip install tox` and tun it:

```
$ tox
```


### Tools and technologies used

* [PEP 3333 - Python WSGI](https://www.python.org/dev/peps/pep-3333/)
* [flask](https://flask.palletsprojects.com/en/1.1.x/)
* [pytest](https://docs.pytest.org/en/latest/)
* [html5lib](https://html5lib.readthedocs.io/en/latest/)

And others – see `requirements.txt`.


### How to watch progress
Unfortunately our progress of development can be watched only in Czech language.

Watch the progress:

* [Youtube playlist](https://www.youtube.com/playlist?list=PLFt-PM7J_H3EU5Oez3ZSVjY5pZJttP2lT)

Other communication channels and info can be found here:
* [Google doc in Czech](https://tinyurl.com/freezeyt)


#### Development blog

We keep a blog about the development of Freezeyt.
Be warned: some of it is in the Czech language.

The blog was tested on Python version 3.8.

The blog is a Flask application.
To run it, install additional dependecies mentioned in
`requirements-blog.txt`.
Then, set the environment variable `FLASK_APP` to the path of the
blog app.
Also set `FLASK_ENV` to "development" for easier debugging.
Then, run the Flask server.

1. On Microsoft Windows:

```shell
> python -m pip install -r requirements-blog.txt
> set FLASK_APP=freezeyt_blog/app.py
> set FLASK_ENV=development
> flask run
```

2. On UNIX:

```shell
$ python -m pip install -r requirements-blog.txt
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
