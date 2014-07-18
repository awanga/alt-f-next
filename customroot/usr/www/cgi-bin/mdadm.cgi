#!/bin/sh

. common.sh
check_cookie
write_header "MDadm setup"

CONFF=/etc/misc.conf

if test -e $CONFF; then
	. $CONFF
fi

if test -z "$MDADM_INTERVAL"; then
	MDADM_INTERVAL=30
fi

SENDTO=$(awk -F= '/^MAILTO/{print $2}' $CONFF)
if test -z "$SENDTO"; then
	msg "Please setup Mail first"
fi

if test -n "$MDADM_EMAIL_TEST"; then testck=checked; fi

cat<<-EOF
	<form action="/cgi-bin/mdadm_proc.cgi" method="post">
	<table>
	<tr><td>Send mail to </td><td><input type=text readonly name=sendto value="$SENDTO">
	Use "Setup Mail" to change</td></tr>
	<tr><td>Check RAID every </td><td><input type=text name=interval value="$MDADM_INTERVAL">
	minutes</td></tr>
	<tr><td>Send test message</td><td><input type=checkbox $testck name=test value="--test">
	Mail a test message when started</td></tr>
	</table>
	<p><input type="submit" name=submit value="Submit">$(back_button)
	</form></body></html>
EOF

