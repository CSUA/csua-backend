import os
import getpass
import shlex
import shutil

from fabric import task


@task
def format(c):
    """Should only be run locally"""
    os.system("black .")

@task
def init(c):
    shutil.copyfile(".env.dev", ".env")
    print("Copied .env.dev -> .env")
    os.system("python manage.py migrate")

@task
def deploy(c):
    sudo_pass = getpass.getpass("sudo password ({}@{}): ".format(c.user, c.host))
    www_data_cmds = [
        "cd /webserver/CSUA-backend",
        "git pull",
        "pip3 install --user -r requirements.txt",
        "python3 manage.py test --keepdb",
        "python3 manage.py collectstatic --noinput",
        "python3 manage.py migrate",
    ]
    c.sudo(
        "bash -c {}".format(shlex.quote(" && ".join(www_data_cmds))),
        user="www-data",
        password=sudo_pass,
    )
    c.sudo("systemctl reload csua-backend-gunicorn", password=sudo_pass)
    c.run("echo Successfully deployed.")
