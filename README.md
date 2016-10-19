CSUA-backend
============

A backend for the CSUA interblags.

## Getting started

1. Install Python 2
2. Install Django with `pip install -r requirements.txt`
3. Change `DEBUG` to `True` at the top of `csua_backend/settings.py`
4. Set up server with `python2 manage.py migrate`
5. Run server with `python2 mangage.py runserver`
6. Navigate to http://127.0.0.1:8000/

## Deploy a new change to git

1. `ssh` into gateway, then `ssh` into www
2. `git pull`
3. `python manage.py collectstatic` to update static images

## Editing/Creating/Deleting Officers

Go to csua.berkeley.edu/admin/ to edit officer data!
