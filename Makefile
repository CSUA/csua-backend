PYTHON = pipenv run python
DEBUG = --debug
MANAGE = $(PYTHON) manage.py $(DEBUG)

default:
	@echo Use make run-dev or make init

.PHONY: run-dev
run-dev:
	$(MANAGE) runserver 0.0.0.0:8000

.PHONY: init
init:
	$(MANAGE) migrate
	$(MANAGE) loaddata db_data-070918 fiber-initial
