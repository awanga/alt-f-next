#!/bin/sh

. common.sh
check_cookie
read_args

#debug

if test "$Submit" = "country"; then
	timezone=$(httpd -d $timezone)
	if test -z "$tz" -o "$timezone" = "Select one Continent/City"; then
		msg "You have to supply a Continent/City and have a valid Timezone field."
	fi
	echo "$(httpd -d $tz)" > /etc/TZ
	echo $timezone > /etc/timezone

elif test "$Submit" = "manual"; then
	if test -z "$hour" -o -z "$date"; then
		msg "You have to supply a Hour and Date."
	fi
	hour=$(httpd -d $hour)
	date=$(httpd -d $date)
	date -s "$date $hour" >& /dev/null
	next="true"

elif test "$Submit" = "ntpserver"; then
	if test -z "$ntps"; then ntps="pool.ntp.org"; fi
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
