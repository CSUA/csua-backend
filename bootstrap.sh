#!/bin/sh
repo_dir=$(dirname $0)

python3 -m venv venv
. venv/bin/activate
pip install -U pip setuptools
pip install poetry
poetry install

if [ ! -e "${repo_dir}/.env" ]; then
    cp "${repo_dir}/.env.dev" "${repo_dir}/.env"
fi
python3 manage.py migrate
pre-commit install
