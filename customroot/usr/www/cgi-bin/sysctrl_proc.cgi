#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/sysctrl.conf

cmd="hi_fan hi_temp lo_fan lo_temp fan_off_temp fan_mode max_fan_speed
	hist_temp warn_temp warn_temp_command crit_temp crit_temp_command mail
	back_button_command front_button_command1 front_button_command2 recovery"

for i in $cmd; do
	arg="$(eval echo \$$i)"
	if test -z "$arg"; then continue; fi
	val=$(httpd -d "$arg")
	echo "$i=\"$val\"" >> $CONFF-
done

mv $CONFF- $CONFF
rcsysctrl reload >& /dev/null

#enddebug
gotopage /cgi-bin/sysctrl.cgi

