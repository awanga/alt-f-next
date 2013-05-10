#!/bin/sh

. common.sh
write_header "Alt-F Login"

#debug

SECR=/etc/web-secret

mktt tt_login "Enter your web administration password,<br>the session will expire after 30 minutes of inactivity."
mktt tt_again "Type your password again. It will be your \"root\" password."

if test -n "$(ls /tmp/check-* 2> /dev/null)" -a ! -f $SECR; then
	cat<<-EOF
		<center><h4><font color=RED>Some filesystems are currently being checked and are not yet available for usage.</font><br>
		You should wait for the check to finish before proceeding.<br>
		You can verify the check evolution in the <em>Filesystem Maintenance</em> section of the Status page.</h4></center>
	EOF
fi

cat<<-EOF
    <center>
	<form name="loginf" action="/cgi-bin/login_proc.cgi" method="post">
    <table>
	<tr><td>Password:</td>
		<td><input type="password" autocomplete="off" name="passwd" $(ttip tt_login)></td>
EOF

if ! test -s $SECR; then
	cat<<-EOF
		</tr>
		<tr><td>Again:</td>
			<td><input type="password" autocomplete="off" name="passwd_again" $(ttip tt_again)></td>
	EOF
fi

cat<<-EOF
		<td><input type="submit" value="Submit"></td>
	</tr>
	</table>
	<input type="hidden" name=from_url value="$QUERY_STRING">
	</form></center>
	<script type="text/javascript">
		document.loginf.passwd.focus();
	</script>
	</body></html>
EOF
