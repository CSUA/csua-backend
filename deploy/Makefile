.PHONY: default deploy clean

default: deploy

remote_user.txt:
	@echo Please enter your CSUA username:
	@read username && echo $$username > $@

USERNAME = $$(cat $<)

deploy: remote_user.txt
	ansible-playbook deploy.yml -i hosts -K -u $(USERNAME)

clean:
	rm remote_user.txt
