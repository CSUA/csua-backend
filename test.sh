#!/bin/bash
# test.sh
HERE=$(dirname $0)
export PIPENV_PIPFILE=$HERE/Pipfile
# currently does not work without --debug due to test db not working
pipenv run python $HERE/manage.py --debug test
