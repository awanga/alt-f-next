#!/bin/sh

. common.sh
check_cookie
write_header "MDadm setup"

CONFF=/etc/mdadm2.conf
CONFM=/etc/msmtprc

if test -e $CONFF; then
	. $CONFF
fi

if test -e $CONFM; then
	SENDTO=$(awk '/^from/{ print $2}' $CONFM)
fi

#back=$(echo $HTTP_REFERER | sed -n 's|.*/cgi-bin/||p')

if test -n "$TEST"; then testck=checked; fi

cat<<-EOF
	<form action="/cgi-bin/mdadm_proc.cgi" method="post">
	<table>
	<tr><td>Send mail to </td><td><input type=text readonly name=sendto value="$SENDTO">
	Use "Mail Setting" to change</td></tr>
	<tr><td>Interval checking </td><td><input type=text name=interval value="$INTERVAL">
	seconds</td></tr>
	<tr><td>Send test message</td><td><input type=checkbox $testck name=test value="--test">
	Mail a test message when started</td></tr>
	<tr><td></td><td><input type="submit" name=submit value="Submit">
		<input type=submit value="Back">
		<input type=hidden name=back value="back"></td></tr>
	</table></form></body></html>
EOF

