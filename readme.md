HawkPost
========

**Warning:** This project is in pre-alpha state. This means it is not 100% ready and you should **use it at your own risk**.

Rationale: For many web and mobile development studios, no matter how hard they try to secure their client secrets (passwords, API keys, etc), the weakest link resides on the client most of the times, specially when he's not a tech savvy person. This project tries to help minimize this issue on the communication between both parties.

HawkPost lets you create unique links that you can share with the person that desires to send you important information but doesn't know how to deal with PGP.

The way it works is like this:

* It fetches your public key

* When the box is open and the secrets submitted, all the content is encrypted on the client side. 

* The server then signs (not implemented yet) the encrypted content

* Finally the server forwards it to your email address.

You can deploy your own server using the code from this repository or use the official server (that is running an exact copy of this repo) at [https://hawkpost.co](https://hawkpost.co).


# Getting started

In this section you can find the steps to setup a minimal development environment on your machine.

Base requirements:

* Python 3
* Redis
* PostgreSQL

## Linux

On a **Debian** based operation execute the following steps, after cloning the repository:

* Install VirtualEnv and VirtualEnvWrapper

> sudo apt-get install python-virtualenvwrapper

(follow their installation steps)

* Create a virtual environment, using python3

> mkvirtualenv hawkpost --python=python3

* Install the dependencies

> pip install -r requirements_dev.txt

* Create the local postgreSQL database with your user and no password

* Migrate the database

> python manage.py migrate

* Check that everything is working

> python manage.py runserver

> celery -A hawkpost worker --beat -l info

## OSX

First, install [Postgres.app](http://postgresapp.com/) and make sure it's in the Applications folder. Add `/Applications/Postgres.app/Contents/Versions/latest/bin` to your $PATH.

Steps:

* Update [Homebrew](http://brew.sh/)

> brew update

* Update [Pip](https://pip.pypa.io/en/stable/installing/)

> sudo pip install --upgrade pip

* Install the latest 2.7.x version and 3.x of Python via Homebrew

> brew install python

> brew install python3

* Install Virtualenv

> pip install virtualenv

* Setup Virtualenv

> mkdir ~/.virtualenvs

> cd ~/.virtualenvs

> virtualenv hawkpost --python=python3

> source hawkpost/bin/activate

* Clone the project, go to the folder and install the dependencies

> pip install -r requirements_dev.txt

* Create the database for the first time

> psql CREATE DATABASE hawkpost_dev;

* Prepare the database

> python manage.py migrate

* Check that everything is working

> python manage.py runserver

> celery -A hawkpost worker --beat -l info 


# Contributing

Given this is an unfinished project and many features are still missing, you are more than welcome to join in and help improve HawkPost. The project will mostly use the Github issues to keep track of bugs, feature requests and milestones. So and account should be all you need to start contributing.

Below are a few things we follow and would appreciate if you do to.

## How to add/remove dependencies

* Add/remove to the correct `.in` file the required package. For dev only dependencies `requirements_dev.in`, otherwise `requirements.in`. Note: you should pin the version number.

* Compile the new requirements (You will need to install `pip-tools`)

> pip-compile requirements.in

and 

> pip-compile requirements.in requirements_dev.in -o requirements_dev.txt

* Commit these changes alongside your code changes


# Credits

![Whitesmith](http://i.imgur.com/Si2l3kd.png)

This project was born during an internal hackathon at [Whitesmith](https://whitesmith.co), which is helping and supporting the current development.
