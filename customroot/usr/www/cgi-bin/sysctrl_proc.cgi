#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/sysctrl.conf

cmd="hi_fan hi_temp lo_fan lo_temp fan_off_temp max_fan_speed
	warn_temp warn_temp_command crit_temp crit_temp_command mail
	back_button_command front_button_command1 front_button_command2 recovery"

if test -f $CONFF; then
	rm $CONFF
fi

for i in $cmd; do
	arg="$(eval echo \$$i)"
	val=$(httpd -d "$arg")
	echo "$i=\"$val\"" >> $CONFF
done

if ! test rcsysctrl status >& /dev/null; then
	rcsysctrl reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/sysctrl.cgi

