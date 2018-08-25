PYTHON = python3
DEBUG = --debug
MANAGE = $(PYTHON) manage.py $(DEBUG)

.PHONY: run-dev
run-dev:
	$(MANAGE) runserver 0.0.0.0:8000

.PHONY: init
init:
	$(MANAGE) migrate
	$(MANAGE) loaddata db_data-070918 fiber-initial

