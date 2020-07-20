# freezeyt
Generator of static web pages created by the Czech Python community.


## Project goal
Main goal of this project is to create a versatile freezer to generate static web pages from web application. The freezer aims to be compatible with any Python Web framework. 


## What IS the project about?
The idea is to create a new freezer in order to generate static web pages. It should also help the czech beginner pythonistas who've already taken their first steps with the Python programming language and now they are looking for some real projects where they could not only put their programming skills to the test but also to improve them.


 
### What the project IS NOT about?
I have no idea so far.


## Installation

When you clone the project you can use command below for install all needed requirements:
```
python -m pip install -r requirements.txt
```

List of requirements:
* [html5lib](https://html5lib.readthedocs.io/en/latest/)


It is higly recommended to create a separate virtual environment for this project.


### Installation for testing project

For testing the project it's necessary to install pytest and flask:
```
$ python -m pip install pytest flask
```


## Usage
The project has not been done yet.
Freezer don't generate static pages so far.


## Contributing
Are you interested in this project? Awesome! Anyone who wants to be part of this project and who's willing to help us is very welcome.
Only started with Python? Good news! We're trying to target mainly the beginner Pythonistas who are seeking opportunities to contribute to (ideally open source) projects and who would like to be part of an open source community which could give them a head start in their (hopefully open source :)) programming careers.
Soo, what if I already have some solid Python-fu? First, there's always something new to learn, and second, we'd appreciate if you could guide the "rookies" and pass on some of the knowledge onto them.


Contributions, issues and feature requests are welcome.
Feel free to check out [issues](https://github.com/encukou/freezeyt/issues) page if you'd like to contribute.


### How to watch progress
Unfortunately our progress of development can be watched only in Czech language.

We have been using these channels:

* live streaming on [Jitsi](https://meet.jit.si/freezeyt)
* videos from live streaming on [Youtube](https://www.youtube.com/playlist?list=PLFt-PM7J_H3EU5Oez3ZSVjY5pZJttP2lT)
* [Pyvec channel](https://pyvec.slack.com/archives/C0168D5TQ4D) on Slack is `# freezeyt`
* [document](https://docs.google.com/document/d/1iACdWvSJZmKTgu2TBKYA71jGaiqftDZDqYW6c4BoqjE/edit) in Czech where you can find all information about project


### How to contribute

1. Just clone this repository to your local computer:

```
$ git clone https://github.com/encukou/freezeyt
```

2. Then fork this repo to your GitHub account
3. Add your forked repo as a new remote to your local computer:
```
$ git remote add <name_your_remote> https://github.com/<your_username>/freezeyt
```
4. Create new branch at your local computer
```
$ git branch <name_new_branch>
```
5. Switch to your new branch
```
$ git switch <name_new_branch>
```
6. Make some awesome changes in code
7. Push changes to your forked repo on GitHub

```
$ git push <your_remote> <your_new_branch>
```
8. Finally make a pull request from your GitHub account to origin
9. Repeat this process until we will have done amazing freezer


### Used tools

* [PEP 3333 - Python WSGI](https://www.python.org/dev/peps/pep-3333/)
* [flask](https://flask.palletsprojects.com/en/1.1.x/)
* [pytest](https://docs.pytest.org/en/latest/)
* [html5lib](https://html5lib.readthedocs.io/en/latest/)


### Why start this project

The Czech Python community uses a lot of static web pages that are generated from a web application for community purposes e.g. workshops, courses, or meetups.

The community has been so far relying on the following projects ([flask-frozen](https://pythonhosted.org/Frozen-Flask/) and [elsa](https://github.com/pyvec/elsa/)) in order to generate the static web content. The new [freezer](https://github.com/encukou/freezeyt) ought to be used with any arbitrary Python Web application framework ([Flask](https://flask.palletsprojects.com/en/1.1.x/), [Django](https://www.djangoproject.com/), [Tornado](https://www.tornadoweb.org/en/stable/), etc.)


## Authors
See GitHub history for all [contributors](https://github.com/encukou/freezeyt/graphs/contributors).


## License
For purposes of this project the [MIT License](LICENCE.MIT) has been chosen.
