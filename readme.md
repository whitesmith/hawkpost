Postbox
=======

Rationale: For many web and mobile development studios, no matter how hard they try to secure their client secrets (passwords, API keys, etc), the weakest link resides on the client, most of the times when he's not a tech savvy person. This project tries to help minimize this issue on the communication between both parties.

Postbox lets you create unique links that you can share with the person that desires to send you important information but doesn't know how to deal with PGP.

The way it works is like this:

* it fetches your public key

* when the box is open and the secrets submitted, all the content is encrypted on the client side. 

* then the server signs the content and forwards it to the box creator email address.


# Getting started

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

*Optional 

# How to add/remove dependencies

* Add/remove to the correct `.in` file the required package. For dev only dependencies `requirements_dev.in`, otherwise `requirements.in`. Note: you should pin the version number.

* Compile the new requirements *

> pip-compile requirements.in

and 

> pip-compile requirements.in requirements_dev.in -o requirements_dev.txt

* Commit these changes alongside your code changes

*You will need to install pip-tools

> pip install pip-tools
