#!/bin/sh

. common.sh
check_cookie
write_header "cron Setup"

#CONF_CRON=/var/spool/cron/crontabs/root

mktt wday_tt "Week day(s) to execute the command.<br><br>0-Sun, 1-Mon, 2-Tue...<br>0,2,4 means Sun, Tue and Thu<br>0-2 means Sun, Mon and Tue<br>* means everyday.<br>No spaces allowed, no checks done"
mktt hour_tt "Hour of the day to execute the command, 0..23.<br><br>Use the same format as in the \"When\" field."

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
	fi
	inp="<input type=checkbox $chkdis name=dis_$i>"

	altf_cron=""
	if echo $cmd | grep -q "#!#"; then
		altf_cron="readonly style=\"color:gray;\""
		cmd=$(echo $cmd | sed -n 's/#.*$//p')
		inp=""		 
	fi

	cat<<-EOF
		<tr><td>$inp<input type=hidden name=altf_$i value=$altf_cron></td>
		<td><input type=text $altf_cron size=6 name=weekday_$i value="$weekday" $(ttip wday_tt)></td>
		<td><input type=text $altf_cron size=6 name=hour_$i value="$hour" $(ttip hour_tt)></td>
		<td><input type=text $altf_cron size=40 name=cmd_$i value="$cmd"></td></tr>
	EOF
	i=$((i+1))
done < $TF

for j in $(seq $i $((i+2))); do 
	cat<<-EOF
		<tr><td><input type=checkbox name=dis_$j></td>
		<td><input type=text size=6 name=weekday_$j value="" $(ttip wday_tt)></td>
		<td><input type=text size=6 name=hour_$j value="" $(ttip hour_tt)></td>
		<td><input type=text size=40 name=cmd_$j value=""></td></tr>
	EOF
	j=$((j+1))
done

cat<<-EOF
	<tr><td><input type=hidden name=cron_cnt value="$((j-1))"><br></td></tr>
	<tr><td colspan=2>$(back_button)<input type=submit name=submit value="Submit"></td></tr>
	</table></form></body></html>
EOF

rm $TF
