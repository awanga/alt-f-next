#!/bin/sh

. common.sh
check_cookie
write_header "Cryptsetup Setup"

CONFF=/etc/misc.conf

if test -f $CONFF; then
	. $CONFF
fi

mktt crypt_tt "Location of file with the encrypt password.<br>
Should be on removable medium,<br>
not on the same disk or box as the encrypted filesystem."

cat<<-EOF
	<form id="cryptf" action="/cgi-bin/cryptsetup_proc.cgi" method="post">
	<table>
	<tr><td>Key file:</td><td><input type=text name="keyfile" value="$CRYPT_KEYFILE" $(ttip crypt_tt)></td></tr>
	<tr><td></td><td><input type="submit" value="Submit">$(back_button)</td></tr>
	</table></form></body></html>
EOF


