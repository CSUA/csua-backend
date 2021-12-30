#!/bin/bash

while getopts "u" opt; do
	case "$opt" in
		u)  unix_socket=1
			;;
	esac
done
repo_dir=$(dirname $0)
python="${repo_dir}"/venv/bin/python3
port=8000

# For soda web hosting
if [ "$unix_socket" = "1" ]; then
	socket=$HOME/public_html/csua-backend.sock
	read LOWERPORT UPPERPORT < /proc/sys/net/ipv4/ip_local_port_range
	port="`shuf -i $LOWERPORT-$UPPERPORT -n 1`"
	rm -vf $socket
	socat UNIX-LISTEN:$socket,fork,mode=777 TCP:localhost:$port &
	echo "Listening on http://csua-backend.$USER.soda.csua.berkeley.edu"
else
	if [ $HOSTNAME = "soda" ]; then
		echo "For easier use on soda consider using $0 -u"
	fi
fi

"${python}" manage.py runserver localhost:$port
