#!/bin/sh
repo_dir=$(dirname $0)
python="${repo_dir}"/venv/bin/python3
pre_commit="${repo_dir}"/venv/bin/pre-commit

python3 -m venv venv
source venv/bin/activate
pip install pipx
pipx install poetry
poetry install

if [ ! -e "${repo_dir}/.env" ]; then
    cp "${repo_dir}/.env.dev" "${repo_dir}/.env"
fi
python3 manage.py migrate
./venv/bin/pre-commit install
