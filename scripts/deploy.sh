HERE=$(dirname $0)
KEYFILE=$HERE/id_rsa
BRANCH=master
ssh www-data@tap.csua.berkeley.edu -i $KEYFILE '
	cd /webserver/csua-backend \
	&& git pull origin $BRANCH \
	&& venv/bin/python manage.py test --keepdb --noinput \
	&& venv/bin/python manage.py migrate --noinput \
	&& venv/bin/python manage.py collectstatic --noinput \
	&& sudo systemctl restart csua-backend-gunicorn \
	&& echo done'
