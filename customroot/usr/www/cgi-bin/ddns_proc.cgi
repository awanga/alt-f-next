#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

read_args
check_cookie

#debug

CONFF=/etc/inadyn.conf
SSCRIPT=/etc/init.d/S75ddns

case $provider in
	dyndns.org) ddns=dyndns@dyndns.org ;;
	zoneedit.com) ddns=default@zoneedit.com ;;
	no-ip.com) ddns=default@no-ip.com ;;
	freedns.afraid.org) ddns=default@freedns.afraid.org ;;
	*) ddns="" ;;
esac

if test -n "$ddns" -a -n "host"; then
	host="$(httpd -d $host)"

	cat<<-EOF > $CONFF
		dyndns_system $ddns
		alias $host
		username $user
		password $passwd
		background
		syslog
		verbose 0
		update_period_sec 60
	EOF
	chmod og-rw $CONFF
fi

#enddebug
gotopage /cgi-bin/net_services.cgi
