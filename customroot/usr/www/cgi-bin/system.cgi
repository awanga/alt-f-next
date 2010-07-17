#!/bin/sh

. common.sh
check_cookie

write_header "System utilities"

cat<<-EOF
	<form action="/cgi-bin/system_proc.cgi" method="post">

	<input type=submit name=action value=Reboot><br><br>

	<input type=submit name=action value=Poweroff><br><br>

	<input type=submit name=action value=KernelLog><br><br>

	<input type=submit name=action value=SystemLog><br><br>

	<input type=submit name=action value=ClearPrintQueues><br><br>

	Services: 
	<input type="submit" name="action" value="StartAll">
	<input type="submit" name="action" value="StopAll">
	<input type="submit" name="action" value="RestartAll"><br><br>

	Current Password:<input type="password" autocomplete="off" name="passwd" value="">
	<input type="submit" name=action value="ChangePassword"><br><br>

	</form></body></html>
EOF

