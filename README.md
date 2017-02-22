CSUA-backend
============

A backend for the CSUA interblags.

## Getting started

1. Install Python 2
2. Install Django with `pip install -r requirements.txt`
3. Change `DEBUG` to `True` at the top of `csua_backend/settings.py`
4. Create database file with `mkdir data` and `touch data/csua.sqlite3`
5. Set up server with `python2 manage.py migrate`
6. Run server with `python2 manage.py runserver`
7. Navigate to http://127.0.0.1:8000/

If you want to visit the admin page at http://127.0.0.1:8000/admin/

8. Create admin user with `python2 manage.py createsuperuser`

## Deploy a new change to git

1. `ssh` into gateway, then `ssh` into www
2. `git pull`
3. `python manage.py collectstatic` to update static images

## Editing/Creating/Deleting Officers

Go to csua.berkeley.edu/admin/ to edit officer data!
