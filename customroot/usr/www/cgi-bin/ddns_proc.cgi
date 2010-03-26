#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

read_args
check_cookie

#debug

CONFF=/etc/inadyn.conf
SSCRIPT=/etc/init.d/S75ddns

case $provider in
	dyndns.org)
                ddns=dyndns@dyndns.org ;;
	zoneedit.com)
        	ddns=default@zoneedit.com ;;
        no-ip.com)
        	ddns=default@no-ip.com ;;
        freedns.afraid.org)
        	ddns=default@freedns.afraid.org ;;
	*)
		ddns=""
esac

if test -n "$ddns" -a -n "host"; then
	host=$(echo $host | sed 's/%2C/,/')

	echo -e dyndns_system $ddns \\n\
	alias $host \\n\
	username $user \\n\
	password $passwd \\n\
	background \\n\
	syslog \\n\
	verbose 0 \\n\
	update_period_sec 60 \\n\
	> $CONFF
fi

#enddebug
gotopage /cgi-bin/net_services.cgi
