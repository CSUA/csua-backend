BRANCH=master
ssh \
    -o StrictHostKeyChecking=no \
    www-data@tap.csua.berkeley.edu \
    'cd /webserver/csua-backend \
	&& git pull origin $BRANCH \
	&& venv/bin/python manage.py test --keepdb --noinput \
	&& venv/bin/python manage.py migrate --noinput \
	&& venv/bin/python manage.py collectstatic --noinput \
	&& sudo systemctl restart csua-backend-gunicorn \
	&& echo done'
