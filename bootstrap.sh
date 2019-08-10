#!/bin/sh
repo_dir=$(dirname $0)
python="${repo_dir}"/venv/bin/python3

python3 -m virtualenv venv
venv/bin/pip3 install -r requirements.txt
if [ ! -e "${repo_dir}/.env" ]; then
    cp "${repo_dir}/.env.dev" "${repo_dir}/.env"
fi
"${python}" manage.py migrate
