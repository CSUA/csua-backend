FROM python:3.5

WORKDIR /app
RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev
COPY manage.py Pipfile.lock Pipfile /app/
RUN pip install pipenv && pipenv install --ignore-pipfile --dev --system

COPY apps apps
COPY templates templates
RUN python manage.py collectstatic --noinput

EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "apps.csua_backend.wsgi"]
