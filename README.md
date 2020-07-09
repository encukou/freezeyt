# freezeyt
Generator of static web pages created by the Czech community of PyLadies.


## Table of contents
* [Project goal](#Project-goal)
* [What is the project about?](#What-is-the-project-about?)
    * [What is NOT the project about?](#What-is-NOT-the-project-about?)
* [Installation](#Installation)
* [Usage](#Usage)
* [Contributing](#Contributing)
    * [How to start contribute](#How-to-contribute)
* [Authors](#Authors)
* [Licence](#Licence)
    


## Project goal
Main goal of this project is to create a versatile freezer to generate static web pages from web application. The freezer aims to be compatible with any Python Web framework. 


## What IS the project about?
The idea is to create a new freezer in order to generate static web pages. It should also help PyLadies who've already taken their first steps with the Python programming language and now they are looking for some real projects where they could not only put their programming skills to the test but also to improve them.

The Czech community PyLadies has used a lot of static web pages that were generated from a web application for community purposes  e.g. workshops, courses, or meetups.

The community has been so far relying on the following projects in order to generate the static web content:

* [flask-frozen](https://pythonhosted.org/Frozen-Flask/)
* community module [elsa](https://github.com/pyvec/elsa/)



The new freezer ought to be based on the old elsa one, but such that it can be used with an arbitrary Python Web application framework, e.g.:

* [Django](https://www.djangoproject.com/)
* [Tornado](https://www.tornadoweb.org/en/stable/)
* etc.
 
### What the project IS NOT about?
I have no idea so far.

## Installation
It is higly recommended to create your own virtual enviroment for this project.

For testing the project it's necessary to install pytest:
```
$ python -m pip install pytest
```

The web application itself will be created by flask:
```
$ python -m pip install flask
```



## Usage

Tools used in this project:
* [PEP 3333 - Python WSGI](https://www.python.org/dev/peps/pep-3333/)
* [flask](https://flask.palletsprojects.com/en/1.1.x/)
* [pytest](https://docs.pytest.org/en/latest/)

## Contributing
Are you interested in this project ? Awesome! Anyone who wants to be part of this project and who's willing to help us is very welcome.
Only started with Python? Good news! We're trying to target mainly the beginner Pythonistas who are seeking opportunities to contribute to (ideally open source) projects and who would like to be part of an open source community which could give them a head start in their (hopefully open source :)) programming careers.
Soo, what if I already have some solid Python-fu? First, there's always something new to learn, and second, we'd appreciate if you could guide the "rookies" and pass on some of the knowledge onto them.


Contributions, issues and feature requests are welcome.
Feel free to check out [issues](https://github.com/encukou/freezeyt/issues) page if you'd like to contribute.

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
7. Push changes to your forked repo in GitHub

```
$ git push <your_remote> <your_new_branch>
```
8. Finally make a pull request from your GitHub account to origin
9. Repeat this process until we will have done amazing freezer


## Authors
Idea of this project occurred to encukou. He is one of the founders of Czech PyLadies.
* [encukou GitHub](https://github.com/encukou)

Also every contributors help to create this module.

## License
For purposes of this project the Massachusetts Institute of Technology License [(MIT)](LICENSE) has been chosen.