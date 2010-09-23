#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/misc.conf

if test -z "$interval" -o -n "$(echo $interval | sed -n 's/[0-9]*//p')"; then
	msg "Interval must be numeric"
fi

sed -i '/^MDADM_/d' $CONFF >& /dev/null

echo MDADM_EMAIL_TEST="$test"  >> $CONFF
echo MDADM_INTERVAL="$interval" >> $CONFF

#enddebug
gotopage /cgi-bin/sys_services.cgi

