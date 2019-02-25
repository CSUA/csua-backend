#!/bin/bash
# deploy.sh: script for quickly deploying master onto tap
USERNAME_FILE=my_csua_username.txt
if ! [ -f $USERNAME_FILE ]; then
	read -p "Enter your CSUA username: " CSUA_UNAME
	echo $CSUA_UNAME > $USERNAME_FILE
fi
CSUA_UNAME=$(cat $USERNAME_FILE)
CSUA_HOST=tap.csua.berkeley.edu


echo "Logging into $CSUA_HOST and running prod_deploy.sh"
ssh -t $CSUA_UNAME@$CSUA_HOST sudo /webserver/CSUA-backend/deploy.sh

# vim: sw=2:et:sts=2
