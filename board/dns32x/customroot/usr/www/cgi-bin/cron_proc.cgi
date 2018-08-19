#!/bin/sh

. common.sh
check_cookie
read_args

#debug

TF=$(mktemp cron-XXXXXX)

for i in $(seq 1 $cron_cnt); do

	eval weekday="\$weekday_$i"
	weekday=$(httpd -d "$weekday")
	if test "${weekday:0:1}" = "d"; then
		mday=${weekday:1}
		weekday='*'
	else
		mday='*'
	fi

	eval hour="\$hour_$i"
	hourmin=$(httpd -d "$hour")
	if echo $hourmin | grep -q ':'; then
		hour=${hourmin%%:*}
		if test -z "$hour"; then hour='*'; fi
		min=${hourmin##*:}
		if test -z "$min"; then min='0'; fi
	else
		hour=$hourmin
		min=0
	fi

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

	echo "${dis}$min $hour $mday * $weekday $cmd $cmt" >> $TF
done

crontab $TF
rm $TF

#enddebug
gotopage /cgi-bin/sys_services.cgi

