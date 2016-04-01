Postbox
=======

**Warning:** This project is in pre-alpha state. This means it is not 100% ready and you should use it at your own risk.

Rationale: For many web and mobile development studios, no matter how hard they try to secure their client secrets (passwords, API keys, etc), the weakest link resides on the client, most of the times when he's not a tech savvy person. This project tries to help minimize this issue on the communication between both parties.

Postbox lets you create unique links that you can share with the person that desires to send you important information but doesn't know how to deal with PGP.

The way it works is like this:

* it fetches your public key

* when the box is open and the secrets submitted, all the content is encrypted on the client side. 

* then the server signs the content and forwards it to the box creator email address.


# Getting started

## Linux

For now, here is the base info on how to setup the development environment on an Debian machine:

Other requirements:

* Postgres

Steps:

* Install VirtualEnv and VirtualEnvWrapper

> sudo apt-get install python-virtualenvwrapper

(follow their installation steps)

* Create a virtual environment, using python3

> mkvirtualenv postbox --python=python3

* Install dependencies

> pip install -r requirements_dev.txt

* Create the local postgres database with your user and no password

* Migrate the database

> python manage.py migrate

* Check that everything is working

> python manage.py runserver

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
> virtualenv postbox --python=python3
> cd postbox
> source bin/activate

* Clone the project, go to the folder and install the dependencies

> pip install -r requirements_dev.txt

*Optional 

## How to add/remove dependencies

* Add/remove to the correct `.in` file the required package. For dev only dependencies `requirements_dev.in`, otherwise `requirements.in`. Note: you should pin the version number.

* Compile the new requirements *

> pip-compile requirements.in

and 

> pip-compile requirements.in requirements_dev.in -o requirements_dev.txt

* Commit these changes alongside your code changes

*You will need to install pip-tools

> pip install pip-tools

# Start the server

## Database

* Create the database for the first time

> psql CREATE DATABASE postbox_dev;

* Prepare the database

> python manage.py migrate

## Run

> python manage.py runserver
