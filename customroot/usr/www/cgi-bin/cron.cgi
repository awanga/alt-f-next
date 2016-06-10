#!/bin/sh

. common.sh
check_cookie

LOCAL_STYLE='.cron {color:gray;}'
write_header "cron Setup"

#CONF_CRON=/var/spool/cron/crontabs/root

mktt wday_tt "Week or Month day(s) to execute the command.<br><br><strong>Week day</strong>: 0-Sun, 1-Mon, 2-Tue...<br>0,2,4 means Sun, Tue and Thu<br>0-2 means Sun, Mon and Tue<br>* means everyday.<br><br><strong>Month day:</strong> first character must be a 'd',<br> 1 to 31 allowed, same rules as above applies,<br> e.g., 'd1,15' or 'd1-5' or 'd28' are valid.<br><br>No spaces allowed, no checks done"
mktt hour_tt "'Hour' or 'Hour:Minute' or ':Minute' of the day to execute the command, 0..23:0..59.<br><br>Use the same format for hour and minute as in the \"When\" field."

if ! rccron status >& /dev/null; then
	rccron start >& /dev/null
fi

TF=$(mktemp cron-XXXXXX)
crontab -l > $TF

cat<<-EOF
	<form id=user name=cronf action=cron_proc.cgi method="post">
	<table><tr><th>Disable</th><th>When</th><th>At</th><th>Command</th></tr>
EOF

i=1
while read min hour monthday month weekday cmd; do
	chkdis=""
	if test "${min:0:1}" = "#"; then
		chkdis="checked"
		min=${min:1}
	fi
	if test "$monthday" != '*'; then
		weekday="d$monthday"
	fi

	inp="<input type=checkbox $chkdis name=dis_$i>"

	altf_cron=""
	if echo "$cmd" | grep -q "#!#"; then
		altf_cron="readonly class=\"cron\""
		cmd=$(echo "$cmd" | sed -n 's/#.*$//p')
		inp=""		 
	fi

	cat<<-EOF
		<tr><td align="center">$inp<input type=hidden name=altf_$i value=$altf_cron></td>
		<td><input type=text $altf_cron size=10 name=weekday_$i value="$weekday" $(ttip wday_tt)></td>
		<td><input type=text $altf_cron size=10 name=hour_$i value="$hour:$min" $(ttip hour_tt)></td>
		<td><input type=text $altf_cron size=40 name=cmd_$i value=$(httpd -e "$cmd")></td></tr>
	EOF
	i=$((i+1))
done < $TF

for j in $(seq $i $((i+2))); do 
	cat<<-EOF
		<tr><td align="center"><input type=checkbox name=dis_$j></td>
		<td><input type=text size=10 name=weekday_$j value="" $(ttip wday_tt)></td>
		<td><input type=text size=10 name=hour_$j value="" $(ttip hour_tt)></td>
		<td><input type=text size=40 name=cmd_$j value=""></td></tr>
	EOF
	j=$((j+1))
done

cat<<-EOF
	</table>
	<p><input type=hidden name=cron_cnt value="$((j-1))">
	<input type=submit name=submit value="Submit">$(back_button)
	</form></body></html>
EOF

rm $TF
