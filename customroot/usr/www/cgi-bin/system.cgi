#!/bin/sh

. common.sh
check_cookie

write_header "System utilities"

cat<<-EOF
	<form action="/cgi-bin/system_proc.cgi" method="post">

	<input type=submit name=action value=Reboot><br>

	<input type=submit name=action value=Poweroff><br>

	<input type=submit name=action value=ClearPrintQueues><br>

	<input type=submit name=action value=KernelLog><br>

	<input type=submit name=action value=SystemLog><br>

	<input type="submit" name=action value="ChangePassword">	
	Current Password:<input type="password" autocomplete="off" name="passwd" value=""><br>

	</form></body></html>
EOF

