#!/bin/sh

. common.sh

check_cookie
read_args

CONFF=/etc/httpd.conf

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK

remip=$(httpd -d $remip)
nip=$(echo $remip | cut -d/ -f1)
nnetwork=$(echo $remip | cut -d/ -f2)

#debug

if test "$nnetwork" = "$NETWORK"; then
	msg "All hosts from the local network are already\n\
allowed to access the administrative web pages.\n\n\
Specify, if needed, an external IP address that\n\
you wish to also have access to the administrative web pages.\n"
fi

if ! checkip $nip; then
	msg "The IP must be in the form x.x.x.x, where x is from 1 to 3 digits, or x.x.x.x/y.y.y.y"
fi

if grep -q '^A:.*#!# Allow remote.*' $CONFF; then
	sed -i "s|^A:.*#!# Allow remote.*$|A:$remip #!# Allow remote|" $CONFF
else
	echo "A:$remip #!# Allow remote" >> $CONFF
fi

#enddebug
gotopage /cgi-bin/http.cgi 
