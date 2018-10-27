PYTHON = python3
DEBUG = --debug
MANAGE = $(PYTHON) manage.py $(DEBUG)

default:
	@echo Use make deploy or make deploy-dev

.PHONY: run-dev
run-dev:
	$(MANAGE) runserver 0.0.0.0:8000

.PHONY: init
init:
	$(MANAGE) migrate
	$(MANAGE) loaddata db_data-070918 fiber-initial

remote_user.txt:
	@echo Please enter your CSUA username:
	@read username && echo $$username > $@

USERNAME = $$(cat $<)

.PHONY: deploy
deploy: deploy/remote_user.txt
	ansible-playbook deploy/deploy.yml -i deploy/hosts -K -u $(USERNAME)

.PHONY: deploy-dev
deploy-dev: deploy/remote_user.txt
	ansible-playbook deploy/deploy-dev.yml -i deploy/hosts -K -u $(USERNAME)

.PHONY: clean
clean:
	rm deploy/remote_user.txt
