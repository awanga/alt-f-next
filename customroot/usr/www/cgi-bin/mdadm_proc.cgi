#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/mdadm2.conf

if test -z "$submit"; then
	gotopage /cgi-bin/sys_services.cgi
	exit
else
	sendto=$(httpd -d $sendto)
	if test -z "$interval" -o -n "$(echo $interval | sed -n 's/[0-9]*//p')"; then
		msg "Interval must be numeric"
	fi

	echo -e "# mdadm --monitor options\nSENDTO=$sendto\nTEST=$test\nINTERVAL=$interval" > $CONFF
fi

#enddebug
gotopage /cgi-bin/mdadm.cgi

