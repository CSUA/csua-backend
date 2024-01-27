BRANCH=master

cd /webserver/csua-backend \
	&& git pull origin $BRANCH \
	&& venv/bin/pip install -r requirements.txt --upgrade \
	&& venv/bin/python manage.py test --keepdb --noinput \
	&& venv/bin/python manage.py migrate --noinput \
	&& venv/bin/python manage.py collectstatic --noinput \
	&& sudo systemctl restart csua-backend-gunicorn \
	&& echo done
