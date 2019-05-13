#!/bin/bash
# prod_migrate.sh
# should be run on the server
HERE=$(dirname $0)
python3 $HERE/manage.py migrate
