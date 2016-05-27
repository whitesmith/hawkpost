HawkPost
========

**Warning:** This project is in `alpha` state. This means it is not 100% ready and you should **use it at your own risk**.

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


## Docker

To use this approach you need to have [Docker][docker-overview] and
[Docker Compose][docker-compose-overview] installed.
Please note that since **this project uses version 2 of the
[Compose file format][docker-compose-versioning]** you may need
to update your Docker and Docker Compose to their latest versions.

Installation instructions for every platform are available at the
[Docker Engine Documentation][docker-install-docs]. If you use Linux you'll
have to [install Docker Compose][docker-compose-install-docs] manually.

After having the latest Docker and Docker Compose installed, **make the
folder** that will hold the **GPG public keys keyring**:

```
mkdir -p gpg_home
```

Some environment variables need to be set so the application works properly.
**Copy** the provided **[.env.sample](.env.sample)** and name it **`.env`**:

```
cp .env.sample .env
```

Since this setup assumes containers talk to each other some of the variables
need to be set in order to point to the containers' names.

**Edit `.env`** and set the following variables to these values:

```
DB_HOST=db
DB_USER=hawkpost
DB_PASSWORD=hawkpost
REDIS_URL=redis://redis:6379/0
SIGN_KEY=/home/user/.gnupg/key.gpg
SIGN_DIR=/home/user/.gnupg
SIGN_KEY_PASSPHRASE=<your-signing-key-password>
EMAIL_HOST=mail_debug
```

**Don't forget to set the remaining variables** as well.

After setting `.env` correctly, just **run** (you may need to `sudo` depending
on your setup)

```bash
# Run the databases in detached mode to avoid seeing the logs
$ docker-compose up -d db redis

# Perform the migrations
# (using `--rm` to remove the temporary container afterwards)
$ docker-compose run --rm web python manage.py migrate

# Run the web, celery and mail_debug containers
# (`docker-compose up` would log db and redis as well)
$ docker-compose up web celery mail_debug
```

These commands

1. **Run the `db` and the `redis` containers** detached from the console, so
   we're not bothered by their logs while working on the application.
1. **Perform the migrations** using a temporary `web` container; it is removed
   afterwards.
1. **Run the `web`, `celery` and `mail_debug` containers** attached to the
   console. `mail_debug` is optional since it is only used when debugging the
   e-mails being sent.

The `web` container will reload on code changes.

You may access the application by **opening `http://<docker-network-ip>` on
your browser**, which you can find by **running** (you may need to run this as
`root` depending on your setup)

```
CID=$(docker ps | grep 'hawkpost_web' | cut -d ' ' -f 1)
docker inspect -f "{{ .NetworkSettings.Networks.hawkpost_default.Gateway }}" $CID
```

This IP won't change unless you remove every container and the corresponding
network (manually), so you may alias it on your `/etc/hosts` (to something like
`hawkpost.dev`).

**Note:** This approach was not tested on OS X or Windows platforms, so the
network feature may require additional steps.

[docker-overview]: https://www.docker.com/products/docker-engine
[docker-compose-overview]: https://www.docker.com/products/docker-compose
[docker-compose-versioning]: https://docs.docker.com/compose/compose-file/#versioning
[docker-install-docs]: https://docs.docker.com/engine/installation
[docker-compose-install-docs]: https://github.com/docker/compose/releases

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
