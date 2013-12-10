#!/bin/sh

. common.sh
write_header "Alt-F Login"

#debug

SECR=/etc/web-secret

mktt tt_login "Enter your web administration password,<br>the session will expire after 30 minutes of inactivity."
mktt tt_again "Type your password again. It will be your \"root\" password."

if test -n "$(ls /tmp/check-* 2> /dev/null)"; then
	echo "<h4 class=\"warn\">Some filesystems are currently being checked and your data might not yet be available for usage.<br>
	You can verify the check evolution in the <em>Filesystem Maintenance</em> section of the <em>Status page</em>.</h4>"
	if test ! -f $SECR -a -z "$(loadsave_settings -ls)"; then
		echo "<h4 class=\"error\">As this is your first login, you <strong>must</strong> wait for the check to finish before login and proceed with the first time wizard.</h4><br>"
	fi
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
		<td></td></tr>
		<tr><td>Again:</td>
			<td><input type="password" autocomplete="off" name="passwd_again" $(ttip tt_again)></td>
	EOF
fi

cat<<-EOF
	<td><input type="submit" value="Submit"></td></tr>
	</table>
	<input type="hidden" name=from_url value="$QUERY_STRING">
	</form></center>
	<script type="text/javascript">
		document.loginf.passwd.focus();
	</script>
	</body></html>
EOF
