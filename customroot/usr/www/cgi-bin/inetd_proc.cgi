#!/bin/sh

. common.sh
read_args
check_cookie

#debug

ssrvs="$(httpd -d $Submit)"

for i in $ssrvs; do
	serv=$(eval echo \$$i)
	grep -q -e "^$i" /etc/inetd.conf
	st=$?
	if test -z "$serv" -a "$st" = "0"; then
		inetd_change=1
		sed -i s/$i/#$i/ /etc/inetd.conf
	elif test "$serv" = "enable" -a "$st" != "0"; then
		inetd_change=1
		sed -i s/#$i/$i/ /etc/inetd.conf
	fi
done

if test "$inetd_change" = 1; then
	kill -HUP $(pidof inetd)
fi

#enddebug
gotopage /cgi-bin/net_services.cgi

