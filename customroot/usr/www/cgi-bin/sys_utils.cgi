#!/bin/sh

. common.sh
check_cookie

write_header "System utilities"

cat<<-EOF
	<form action="/cgi-bin/sys_utils_proc.cgi" method="post">

	<fieldset><legend><strong>Reboot or Poweroff</strong></legend>
	<input type=submit name=action value=Reboot onClick="return confirm('The box will reboot now.\nWithin 45 seconds you will be connected again.\n\nProceed?')">
	<input type=submit name=action value=Poweroff onClick="return confirm('The box will poweroff now.\n\nProceed?')">
	</fieldset><br>

	<fieldset><legend><strong>View Logs</strong></legend>
	<input type=submit name=action value=KernelLog>
	<input type=submit name=action value=SystemLog>
	</fieldset><br>
	
	<fieldset><legend><strong>Services</strong></legend>
	<input type="submit" name="action" value="StartAll">
	<input type="submit" name="action" value="StopAll">
	<input type="submit" name="action" value="RestartAll">
	</fieldset><br>

	<fieldset><legend><strong>Administering password</strong></legend>
	Current Password:<input type="password" autocomplete="off" name="passwd" value="">
	<input type="submit" name=action value="ChangePassword")>
	</fieldset><br>

	<fieldset><legend><strong>Printers</strong></legend>
	<input type=submit name=action value=ClearPrintQueues>
	</fieldset><br>

	</form></body></html>
EOF

