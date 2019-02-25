#!/bin/bash
# prod_migrate.sh
# should be run on the server
HERE=$(dirname $0)
export PIPENV_PIPFILE=$HERE/Pipfile
pipenv run python $HERE/manage.py migrate
