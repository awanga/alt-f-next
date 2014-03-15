#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

read_args
check_cookie

#debug

CONFF=/etc/inadyn.conf
SSCRIPT=/etc/init.d/S44ddns

sites="dyndns@dyndns.org default@zoneedit.com default@no-ip.com default@freedns.afraid.org
default@easydns.com dyndns@3322.org default@sitelutions.com default@dnsomatic.com ipv6tb@he.net
default@tzo.com default@dynsip.org default@dhis.org default@majimoto.net default@zerigo.com"

provider=$(httpd -d "$provider")

for i in $sites; do
	site=$(echo $i | cut -d"@" -f2)
	if test "$provider" = "$site"; then ddns=$i; fi
done

if test "$ddns" != "default@freedns.afraid.org"; then
	passwd=$(checkpass "$passwd")
	if test $? != 0; then
		msg "$passwd"
	fi
fi

if test -n "$ddns" -a -n "$host"; then
	host=$(httpd -d "$host")

	cat<<-EOF > $CONFF
		dyndns_system $ddns
		alias $host
		username $user
		password $passwd
		syslog
		verbose 0
		update_period_sec 60
	EOF
	chmod og-rw $CONFF
fi

#enddebug
gotopage /cgi-bin/net_services.cgi
