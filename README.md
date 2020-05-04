csua-backend
============

A backend for the CSUA interblags.

Current Maintainer: Robert Quitt <robertq@csua.berkeley.edu>

**JAN 2020: SEEKING NEW MAINTAINER** (I'm graduating -robertq)

## User Workflow

1. Create a fork of this repo
2. Clone your fork to your local/development machine
3. Install dependencies locally
4. Make changes locally, test, repeat
5. Commit those changes
6. Push commits to your fork
7. Make a pull request

## Installation (virtualenv)

1. Install Python 3.6+
2. Create virtualenv `python3 -m `
2. Install Django and dependencies with `venv/bin/pip3 install -r requirements.txt`
3. Create your `.env` file by copying `.env.dev`, e.g. `cp .env.dev .env`
4. Set up local db with `venv/bin/python3 manage.py migrate`
5. Run server with `venv/bin/python3 manage.py runserver`
6. Navigate web browser to http://127.0.0.1:8000/
7. Create admin user with `venv/bin/python3 manage.py createsuperuser`
  - Visit the admin page at http://127.0.0.1:8000/admin/ to add a semester object

### Installation (virtualenv, alternative)

If you're using GNU/Linux, you should be able to use `bootstrap.sh`. In theory, OSX should also work, but it's untested.

## Making changes to database models

1. Make changes to `db_data/models.py`
2. `python3 manage.py makemigrations` on your development machine
3. `python3 manage.py migrate` to apply new migrations to your local db
4. Commit and push your changes to `models.py` as well as generated `migrations/`
5. Pull latest changes on remote machine
6. `python3 manage.py migrate` on remote machine to update database with latest models
7. Run `sudo systemctl reload csua-backend-gunicorn` on the remote machine so the changes take effect

## Editing/Creating/Deleting Data

Go to https://www.csua.berkeley.edu/admin/ to edit data!

## Repo structure

Django's online documentation has more detail on a project's structure

- `apps/`
  - This Django project is divided into "apps" (i.e. `main_page/`, `db_data/`, etc.)
  - `csua_backend/` holds the projects's configurations
  - Each app is divided into:
  	- `migrations/` lists the changes that have been made to the database models
  	- `__init__.py` just tells python the app is a python module
  	- `admin.py` details how db models should be viewed in the admin interface
  	- `apps.py` probably says that this directory is an app
  	- `models.py` contains the database models of the app
  	- `tests.py` has unit tests to test the apps functionality
  	- `urls.py` says what URLs route to which views
  	- `views.py` has functions that serve a "view" (webpage)
- `fixtures/` contains database fixtures to record and bootstrap content and various database data
- `media_root/` is where user-uploaded files are served from
- `requirements.txt` lists the required python packages for this project.
- `static_root/` is where static files are served from (many of which come from `./static/` and are moved here by `manage.py`'s `collectstatic`)
- `templates/` holds the html templates that are populated and served by views
- `manage.py` is a command-line script for performing actions on the project

## Dumping database data into json:

```shell
python3 manage.py dumpdata db_data > fixtures/$(date +db_data-%m%d%y.json)
```

## Deploying

### (Option 1) Deploy a new change from GitHub to tap

1. `ssh` into `tap.csua.berkeley.edu`
2. Change directory to the project directory `/webserver/csua-backend/`
3. `sudo -u www-data git pull`
4. `venv/bin/python manage.py collectstatic` to update static images
5. If you're making changes to the db models, follow those instructions too

### (Option 2) Deploy to tap using fabric

1. `fab -H <user>@tap.csua.berkeley.edu deploy`
2. Profit


## Deployment Details

- This Django app runs as on a `gunicorn` server on `tap`.
- The `gunicorn` process is managed by `systemd` and the service file is located at `/etc/systemd/system/csua-backend-gunicorn.service`
  - This service can be manipulated with `systemctl`
    - To reload the wsgi app, run `sudo systemctl reload csua-backend-gunicorn`
- `tap` runs debian 9.8 (stretch), we are using Python 3.6.
- The app is behind an Nginx proxy.
  - Nginx serves the static and media files, homedirs, and forwards all other requests to the app.
  - <https://github.com/CSUA/services-nginx/blob/master/sites-available/www.csua.berkeley.edu>
  - `/etc/nginx/sites-available/www.csua.berkeley.edu`
- `mysqlclient` is installed and necessary for deployment on `tap`

## LDAP Details

`tap` runs an OpenLDAP server. It is accessible from anywhere over TLS on port 636.

For an LDAP client to connect, it must accept our self-signed certificate.
Usually this is done by adding this line to `/etc/ldap/ldap.conf`:

`TLS_REQCERT allow`
