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
	date -s "$date $hour"
	next="true"

elif test "$Submit" = "ntpserver"; then
	sntp -P no -r $ntps
	next="true"
fi

hwclock -w -u

#enddebug

if test -n "$next" -a -f /tmp/firstboot; then
	gotopage /cgi-bin/newuser.cgi
else
	gotopage /cgi-bin/time.cgi
fi
