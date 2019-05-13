#!/bin/bash
# test.sh
HERE=$(dirname $0)
python3 $HERE/manage.py test --keepdb
