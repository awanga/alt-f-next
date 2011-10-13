#!/bin/sh

. common.sh
check_cookie
read_args

#debug

if test "$Submit" = "country"; then
	echo "$(httpd -d $tz)" > /etc/TZ
	echo "$(httpd -d $timezone)" > /etc/timezone

elif test "$Submit" = "manual"; then
	hour=$(httpd -d $hour)
	date=$(httpd -d $date)
	date -s "$date $hour" >& /dev/null
	next="true"

elif test "$Submit" = "ntpserver"; then
	sntp -s $ntps >& /dev/null
	next="true"
fi

hwclock -w -u >& /dev/null

#enddebug

if test -n "$next" -a -f /tmp/firstboot; then
	if test -d "$(readlink -f /home)"; then
		gotopage /cgi-bin/settings.cgi
	else
		gotopage /cgi-bin/diskwiz.cgi
	fi
else
	gotopage /cgi-bin/time.cgi
fi
