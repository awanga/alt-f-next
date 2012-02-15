#!/bin/sh

. common.sh
check_cookie
read_args

#debug

TF=$(mktemp cron-XXXXXX)

for i in $(seq 1 $cron_cnt); do

	eval weekday="\$weekday_$i"
	weekday=$(httpd -d "$weekday")

	eval hour="\$hour_$i"
	hour=$(httpd -d "$hour")

	eval cmd="\$cmd_$i"
	cmd=$(httpd -d "$cmd")

	if test -z "$weekday" -o -z "$hour" -o -z "$cmd"; then continue; fi

	dis=""
	if test -n "$(eval echo \$dis_$i)"; then
		dis="#"
	fi

	cmt=""
	if test -n "$(eval echo \$altf_$i)"; then
		cmt="#!# Alt-F cron"
	fi

	echo "${dis}0 $hour * * $weekday $cmd $cmt" >> $TF
done

crontab $TF
rm $TF

#enddebug
gotopage /cgi-bin/sys_services.cgi

