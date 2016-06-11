#!/bin/sh

. common.sh
check_cookie
read_args

#debug

if test "$Submit" = "country"; then
	timezone=$(httpd -d "$timezone")
	if test -z "$tz" -o -z "$timezone" -o "$timezone" = "Select one Continent/City"; then
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

elif test "$Submit" = "ntpserver"; then
	if test -z "$ntps"; then ntps="0.pool.ntp.org"; fi
	fsntp -s $ntps >& /dev/null
fi

hwclock -wu >& /dev/null

#enddebug
gotopage /cgi-bin/time.cgi

