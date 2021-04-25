csua-backend
============

A backend for the CSUA interblags.

A Django web app that:

* Hosts our website at https://www.csua.berkeley.edu
  * Displays [information about our club](apps/main_page)
  * Manages and displays [current officers, politburo, sponsors, and events](apps/db_data)
  * Provides [new CSUA account creation](apps/newuser)
  * Provides CSUA account [password resets](apps/password_reset)
  * Provides interface for [managing LDAP groups](apps/ldap)
* Runs a [slack bot](apps/slackbot) on https://csua.slack.com
* Runs a [discord bot](apps/discordbot) on https://www.csua.berkeley.edu/discord
* Tracks [Soda 311 office computer usage](apps/tracker)

Continuous integration/deployment via [Travis CI][travis]:

[![](https://travis-ci.org/CSUA/csua-backend.svg?branch=master)][travis]

[travis]: https://travis-ci.org/github/CSUA/csua-backend

See [issues](https://github.com/CSUA/csua-backend/issues) for a list of TODOs.

## User Workflow

1. (Optional) Create a fork of this repo
    - Do this if you don't have write access
    - If you do have write access, use a new branch instead
2. Clone to your local/development machine
3. Install dependencies
4. Make changes, test, repeat
5. Commit those changes
6. Push commits to your fork/branch
7. Make a pull request

## Installation (venv, manual)

1. Install Python 3.6+
2. Create venv `python3 -m venv venv`
2. Install Django and dependencies with `venv/bin/pip3 install -r requirements.txt`
3. Install pre-commit with `venv/bin/pre-commit install`
4. Create your `.env` file by copying `.env.dev`, e.g. `cp .env.dev .env`
5. Set up local sqlite database with `venv/bin/python3 manage.py migrate`
6. Run server with `venv/bin/python3 manage.py runserver`
  * If on soda, you will have to run `venv/bin/python3 manage.py runserver 0.0.0.0:$PORT` where `$PORT` is between 8000 and 8999, and connect by going to `http://soda.berkeley.edu:$PORT`
7. Navigate web browser to http://127.0.0.1:8000/
8. Create admin user with `venv/bin/python3 manage.py createsuperuser`
    - Visit the admin page at http://127.0.0.1:8000/admin/ to add a semester object

### Installation (venv, automatic)

If you're using GNU/Linux or OSX, use `bootstrap.sh`.

### pre-commit and black

[pre-commit][pre-commit] is a tool that picks up formatting and other issues before making a commit. It will automatically format your python code with [black][black]. This is so that the code is clean and consistent, making it easier to review.

Additionally, I recommend you set up autoformatting with black on-save. If you use vim, you can add this to your .vimrc:
```vimscript
autocmd BufWritePost *.py silent exec "!black <afile>" | exec "redraw!"
```

[pre-commit]: https://pre-commit.com/
[black]: https://black.readthedocs.io/en/stable/

## Making changes to database models

1. Make changes to `db_data/models.py`
2. `venv/bin/python3 manage.py makemigrations` on your development machine
3. `venv/bin/python3 manage.py migrate` to apply new migrations to your local db
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

## Deploying


### (Automatic) Travis CI

Commits to `master` get automatically tested and deployed by Travis CI.
`scripts/id_rsa.enc` is an encrypted ssh key that lets the deploy script log in as `www-data`.
It needs to be decrypted with a secret key which is specified as an environment variable in Travis.

See builds here: https://travis-ci.org/github/CSUA/csua-backend

### Manual Deploy

1. `ssh` into `tap.csua.berkeley.edu`
2. Change directory to the project directory `/webserver/csua-backend/`
3. `sudo -u www-data git pull`
4. `sudo -u www-data venv/bin/python manage.py collectstatic` to update static files
5. `sudo -u www-data venv/bin/python manage.py migrate` to migrate db
6. `sudo -u www-data venv/bin/python manage.py test` to make sure tests pass
7. `sudo systemctl restart csua-backend-gunicorn` to restart server

## Deployment Details

- This Django app runs as a wsgi app on a `gunicorn` server on `tap`.
- The `gunicorn` process is managed by `systemd` and the service file is located at `/etc/systemd/system/csua-backend-gunicorn.service`
  - This service can be manipulated with `systemctl`
    - To reload the wsgi app, run `sudo systemctl reload csua-backend-gunicorn`
- `tap` runs debian 9.8 (stretch), we are using Python 3.6.
- The app is behind an Nginx proxy.
  - Nginx serves the static and media files, homedirs, and forwards all other requests to the app.
  - <https://github.com/CSUA/services-nginx/blob/master/sites-available/www.csua.berkeley.edu>
  - `/etc/nginx/sites-available/www.csua.berkeley.edu`
- `mysqlclient` is installed and necessary for deployment on `tap`

### /etc/sudoers
These changes are here so that the newuser script and deployment script run properly.
If the change, `/etc/sudoers` _may_ also need to be changed.
```
www-data ALL = (root) NOPASSWD: /webserver/csua-backend/apps/newuser/config_newuser
www-data ALL = NOPASSWD: /bin/systemctl restart csua-backend-gunicorn
```

## LDAP Details

`tap` runs an OpenLDAP server. It is accessible from anywhere over TLS on port 636.

For an LDAP client to connect, it must accept our self-signed certificate.
Usually this is done by adding this line to `/etc/ldap/ldap.conf`:

`TLS_REQCERT allow`

## Dumping database data into json:

```shell
python3 manage.py dumpdata db_data > fixtures/$(date +db_data-%m%d%y.json)
```
