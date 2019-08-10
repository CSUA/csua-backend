#!/bin/sh
repo_dir=$(dirname $0)
python="${repo_dir}"/venv/bin/python3
"${python}" manage.py runserver
