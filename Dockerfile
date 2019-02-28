FROM python:3.5

WORKDIR /app
RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev
COPY manage.py Pipfile Pipfile.lock wait-for /app/
RUN pip install pipenv && pipenv install --skip-lock --dev --system

ONBUILD COPY apps apps
ONBUILD COPY templates templates
ONBUILD RUN python manage.py collectstatic --noinput

EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "apps.csua_backend.wsgi"]
