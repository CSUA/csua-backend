CSUA-backend
============

A backend for the CSUA interblags.

## Getting started

1. Install Python 3
2. Install Django and dependencies with `pip3 install --user -r requirements.txt`
3. Change `DEBUG` to `True` at the top of `csua_backend/settings.py`
4. Set up local db with `python3 manage.py migrate`
5. Run server with `python3 manage.py runserver`
6. Navigate web browser to http://127.0.0.1:8000/

If you want to visit the admin page at http://127.0.0.1:8000/admin/

7. Create admin user with `python3 manage.py createsuperuser`

## Deploy a new change to git

Beta feature: instead of doing steps 3-5, simply run
`ansible-playbook deploy.yml -i hosts -K`

1. `ssh` into `tap.csua.berkeley.edu`
2. Change directory to the project directory
3. `git pull`
4. `python3 manage.py collectstatic` to update static images
5. If you're making changes to the db models, follow those instructions too

## Making changes to database models

1. Make changes to `db_data/models.py`
2. `python3 manage.py makemigrations` on your development machine
3. `python3 manage.py migrate` to apply new migrations to your local db
4. Commit and push your changes to `models.py` as well as generated `migrations/`
5. Pull latest changes on remote machine
6. `python3 manage.py migrate` on remote machine to update database with latest models
7. Run 'sudo systemctl reload apache2' on the remote machine so the changes take effect

## Editing/Creating/Deleting Officers

Go to https://www.csua.berkeley.edu:8080/admin/ to edit officer data!

## Repo structure

Django's online documentation has more detail on a project's structure

- `csua_backend/` holds the projects's configurations
- This Django project is divided into "apps" (i.e. `main_page/`, `db_data/`, etc.)
- Each app is divided into:
	- `migrations/` lists the changes that have been made to the database models
	- `__init__.py` just tells python the app is a python module
	- `admin.py` details how db models should be viewed in the admin interface
	- `apps.py` probably says that this directory is an app
	- `models.py` contains the database models of the app
	- `tests.py` has unit tests to test the apps functionality
	- `urls.py` says what URLs route to which views
	- `views.py` has functions that serve a "view" (webpage)
- `media_root/` is where user-uploaded files are served from
- `static_root/` is where static files are served from (many of which come from `main_page/static/` and are moved here by `manage.py`'s `collectstatic`)
- `templates/` holds the html templates that are populated and served by views
- `deploy.yml` is an ansible configuration for deploying the website
- `manage.py` is a command-line script for performing actions on the project
- `requirements.txt` lists the `pip` dependencies of this project