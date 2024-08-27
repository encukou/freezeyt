
# Contributing

Freezeyt is developed on [GitHub](https://github.com/encukou/freezeyt).

Contributions, issues and feature requests are welcome.
Feel free to check out the [issues page] if you'd like to
contribute.

[issues page]: https://github.com/encukou/freezeyt/issues


## Quick guide

1. Clone this repository to your local
   computer:

        $ git clone https://github.com/encukou/freezeyt

2. Then fork this repo to your GitHub account
3. Add your forked repo as a new remote to your local computer:

        $ git remote add <remote_label> https://github.com/<username>/freezeyt

4. Create a new branch at your local computer

        $ git branch <branch_name>

5. Switch to your new branch

        $ git switch <branch_name>

6. Update the code
7. Push the changes to your forked repo on GitHub

        $ git push <remote_label> <branch_name>

8. Finally, make a pull request from your GitHub account to origin


## Installing for development

Freezeyt can be installed from the current directory:

```console
$ python -m pip install -e .
```

It also has several groups of extra dependecies:

* `blog` for the project blog
* `dev` for development and running tests
* `typecheck` for [mypy] type checks

Each group can be installed separately:

```console
$ python -m pip install -e ."[typecheck]"
```

or you can install more groups at once:
```console
$ python -m pip install -e ."[blog, dev, typecheck]"
```

[mypy]: https://www.mypy-lang.org/


## Using an in-development copy of Freezeyt

* Set `PYTHONPATH` to the directory with Freezeyt, for example:
    * Unix: `export PYTHONPATH="/home/name/freezeyt"`
    * Windows: `set PYTHONPATH=C:\Users\Name\freezeyt`

* Install the web application you want to freeze. Either:
    * install the application using `pip`, if possible, or
    * install the application's dependencies and `cd` to the app's directory.

* Run Freezeyt, for example:
    * `python -m freezeyt demo_app_url_for _build --prefix http://freezeyt.test/foo/`



## Tests

For testing the project it's necessary to install additional requirements:

```console
$ python -m pip install .[dev]
```

To run tests in your current environment, use pytest:

```console
$ python -m pytest
```

To run tests with multiple Python versions (if you have them installed),
install `tox` using `python -m pip install tox` and run it:

```console
$ tox
```

### Environ variables for tests

Some test scenarios compare Freezeyt's results with expected output.
When the files with expected output don't exist yet,
they can be created by setting the environment variable
`TEST_CREATE_EXPECTED_OUTPUT` to `1`:

**Unix**

```console
$ export TEST_CREATE_EXPECTED_OUTPUT=1
```

**Windows**

```doscon
> set TEST_CREATE_EXPECTED_OUTPUT=1
```

If you set the variable to any different value or leave it unset
then the files will not be recreated
(tests will fail if the files are not up to date).

When output changes, you need to first delete the expected output,
regenerate it by running tests with `TEST_CREATE_EXPECTED_OUTPUT=1`,
and check that the difference is correct.


## How to watch progress

Unfortunately our progress of development can be watched only in Czech language.

Watch the progress on our [Youtube playlist](https://www.youtube.com/playlist?list=PLFt-PM7J_H3EU5Oez3ZSVjY5pZJttP2lT).

Other communication channels and info can be found
in a [Google doc](https://tinyurl.com/freezeyt) (in Czech).


## Freezeyt Blog

We keep a blog about the development of Freezeyt.
It is available [here](https://encukou.github.io/freezeyt/).

**Be warned:** some of it is in the Czech language.

### Blog development

The blog was tested on Python version 3.8.

The blog is a Flask application.
To run it, install additional dependecies with
`python -m pip install .[blog]` and run the Flask server:

```console
$ python -m pip install .[blog]
$ flask --app freezeyt_blog/app.py run --debug
```

The URL where your blog is running will be printed on the terminal.

Once you're satisfied with how the blog looks, you can freeze it with:

```console
$ python -m freezeyt freezeyt_blog.app freezeyt_blog/build
```

### Adding new articles to the blog

Articles are writen in the `Markdown` language.

**Article** - save to directory `../freezeyt/freezeyt_blog/articles`

**Images to articles** - save to directory `../freezeyt/freezeyt_blog/static/images`

If the files are saved elsewhere, the blog will not work correctly.
