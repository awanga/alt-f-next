#!/bin/sh

. common.sh

check_cookie
read_args

CONFF=/etc/httpd.conf

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
network=$(echo $hostip | awk -F. '{printf "%d.%d.%d.", $1,$2,$3}')
nnetwork=$(echo $remip | awk -F. '{printf "%d.%d.%d.", $1,$2,$3}')

#debug

if test "$nnetwork" = "$network"; then
	msg "All hosts from the local network are already\n\
allowed to access the administering web pages.\n\n\
Specify, if needed, an external IP address that\n\
you wish to also have access to the administering web pages.\n"
fi

if ! checkip $remip; then
	msg "The IP must be in the form x.x.x.x, where x is from 1 to 3 digits."
fi

if test -n "$oldremip"; then
	sed -i '/'$oldremip'/d' $CONFF
fi

if test -n "$remip"; then
	echo "A:$remip" >> $CONFF
fi

#enddebug
gotopage /cgi-bin/http.cgi 
