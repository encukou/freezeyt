# freezeyt
Generator of static web pages created by czech community of PyLadies.


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
Main goal of his project is to create versatile freezer to generate static web pages from web application. Freezer will be compatible with any python framework designate for creation of web-app. 


## What is the project about?
The project is to create new freezer for generate static web pages. The project aim to PyLadies which already done first steps with python and now they are looking for some real project where they can improved their programming skills.

Czech community Pyladies used a lot static web pages generated from web app for purposes of community as workshops, courses or meetsup.

Community have been used this combination for generate static web pages:

* [flask-frozen](https://pythonhosted.org/Frozen-Flask/)
* community module [elsa](https://github.com/pyvec/elsa/)



PyLadies wants to improved old elsa module and create a new one which can be used not only with flask but also with other web app framework as:

* [Django](https://www.djangoproject.com/)
* [Tornado](https://www.tornadoweb.org/en/stable/)
* etc.
 
### What is NOT the project about?
I have no idea so far.

## Installation
It is higly recommended to create your virtual enviroment for this project.

For testing project is necessary to install pytest:
```
$ python -m pip install pytest
```

Web application will be created by flask:
```
$ python -m pip install flask
```



## Usage

Tools used in project:
* [PEP 3333 - Python WSGI](https://www.python.org/dev/peps/pep-3333/)
* [flask](https://flask.palletsprojects.com/en/1.1.x/)
* [pytest](https://docs.pytest.org/en/latest/)

## Contributing
Are you interested about this project ? If you want to be a part of this project everybody is welcome to help us. This project aim to beginner pythonistas. So if you are beginner and looking for some start project in GitHub this is perfect project for you.

Contributions, issues and feature requests are welcome.
Feel free to check [issues](https://github.com/encukou/freezeyt/issues) page if you want to contribute.

### How to contribute


1. Just clone this repository to your local computer:

```
$ git clone https://github.com/encukou/freezeyt
```

2. Then fork this repo to your GitHub account
3. Add your forked repo as a new remote to your local computer:
```
$ git remote add <your_username> https://github.com/<your_username>/freezeyt
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
* [GitHub]((https://github.com/encukou).)

Also every contributors help to create this module.

## Licence
For purposes of this project was choosed Massachusetts Institute of Technology Licence [(MIT)](LICENSE)