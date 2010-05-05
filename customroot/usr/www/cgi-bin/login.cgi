#!/bin/sh

. common.sh
write_header "Alt-F Login"

SECR=/etc/web-secret

cat<<-EOF
    <center><form action="/cgi-bin/login_proc.cgi" method="post">
    <table><tr><td>Password:</td><td> <input type="password" autocomplete="off" name="passwd" ></td>
EOF

if ! test -e $SECR; then
    echo "</tr><tr><td>Again:</td><td> <input type="password" autocomplete="off" name="passwd_again" ></td>"
fi

cat<<-EOF
	<td></td><td><input type="submit" value="Submit"></td>
	<input type="hidden" name=from_url value="$(basename $REQUEST_URI)"></td>
	</tr></table></form></center></body></html>
EOF
