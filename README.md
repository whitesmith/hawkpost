# Hawkpost

Hawkpost lets you create unique links that you can share with the person that desires to send you important information but doesn't know how to deal with PGP.

You can deploy your own server using the code from this repository or use the official server (that is running an exact copy of this repo) at [https://hawkpost.co](https://hawkpost.co).

## Rationale

For many web and mobile development studios, no matter how hard they try to secure their client secrets (passwords, API keys, etc), the weakest link resides on the client most of the times, specially when he's not a tech savvy person. This project tries to help minimize this issue on the communication between both parties.

The way it works is like this:

1. It fetches your public key.
1. When the box is open and the secrets submitted, all the content is encrypted on the client side.
1. The server then signs (**experimental**) the encrypted content.
1. Finally the server forwards it to your e-mail address.

# Setting up a development environment

In this section you can find the steps to setup a minimal development environment on your machine.

Base requirements:

- Python 3
- Redis
- PostgreSQL

## On Linux

On a **Debian** based operating system execute the following steps, after cloning the repository:

* Make sure you have `pipenv` installed. You can check [this page for more information](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv)

- Install the dependencies

```
$ pipenv install
```

- Create the local postgreSQL database with your user and no password

- Migrate the database

```
$ pipenv run python manage.py migrate
```

- Generate stylesheet with gulp (installation instructions for gulp can be found [here](https://gulpjs.com/))

```
$ gulp build
```

- Now you should be able to launch the server and its workers

```
$ pipenv run python manage.py runserver
$ pipenv run celery -A hawkpost worker --beat -l info
```

You can avoid `pipenv run` in every command if you first active the virtual environment with `pipenv shell`.

## Using Docker

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
$ mkdir -p gpg_home
```

Some environment variables need to be set so the application works properly.
**Copy** the provided **[.env.sample](.env.sample)** and name it **`.env`**:

```
$ cp .env.sample .env
```

Since this setup assumes containers talk to each other some of the variables
need to be set in order to point to the containers' names.

**Edit `.env`** and set the following variables to these values:

```
DB_HOST=db
DB_USER=hawkpost
DB_PASSWORD=hawkpost
REDIS_URL=redis://redis:6379/0
```

**Don't forget to set the remaining variables** as well.

After setting `.env` correctly, just **run** (you may need to `sudo` depending
on your setup)

```bash
# Run the databases in detached mode to avoid seeing the logs
$ docker-compose up -d db redis

# Perform the migrations
# (using `--rm` to remove the temporary container afterwards)
$ docker-compose run --rm web pipenv run python manage.py migrate

# Run the web and celery containers
# (`docker-compose up` would log db and redis as well)
$ docker-compose up web celery
```

These commands

1. **Run the `db` and the `redis` containers** detached from the console, so
   we're not bothered by their logs while working on the application.
1. **Perform the migrations** using a temporary `web` container; it is removed
   afterwards.
1. **Run the `web` and `celery`** attached to the
   console.

The `web` container will reload on code changes.

You may access the application by **opening `http://<docker-network-ip>` on
your browser**, which you can find by **running** (you may need to run this as
`root` depending on your setup).

```
CID=$(docker ps | grep 'hawkpost_web' | cut -d ' ' -f 1)
docker inspect -f "{{ .NetworkSettings.Networks.hawkpost_default.Gateway }}" $CID
```

This IP won't change unless you remove every container and the corresponding
network (manually), so you may alias it on your `/etc/hosts` (to something like
`hawkpost.test`).

**Note:** This approach was not tested on OS X or Windows platforms, so the
network feature may require additional steps.

[docker-overview]: https://www.docker.com/products/docker-engine
[docker-compose-overview]: https://www.docker.com/products/docker-compose
[docker-compose-versioning]: https://docs.docker.com/compose/compose-file/#versioning
[docker-install-docs]: https://docs.docker.com/engine/installation
[docker-compose-install-docs]: https://github.com/docker/compose/releases

# Running the test suite

To execute our current test suite, you just need to execute the following command after setting up your local development environment:

> \$ pipenv run python manage.py test

In case you are using our docker setup the command should be:

> \$ docker-compose run --rm web pipenv run python manage.py test

# Credits

![Whitesmith](http://i.imgur.com/Si2l3kd.png)

This project was born during an internal hackathon at [Whitesmith](https://whitesmith.co), which is helping and supporting the current development.
