#!/bin/sh

. common.sh
check_cookie

write_header "System utilities" "document.sysutils.reset()"

mktt ssl_tt "Erases current SSL certificate for https and creates a new one.<br>
WARNING: your browser will complain and you will have to delete<br>
or revoke the old certificate and make the browser accept the new one.<br>
Does not affects the ssh host key."

logsel="<select name=\"logaction\" onchange=\"return submit()\">
<option>Select one</option>
<option value=\"KernelLog\">Kernel Log</option>
<option value=\"SystemLog\">System Log</option>
<option value=\"Processes\">Running Processes</option>"

for i in $(find /var/log/ -name \*.log\* -o -name log.\* -o -name \*_log); do
	logsel="$logsel<option value=$i>$(basename $i | sed -r 's/(\.log|log\.|_log)//g')</option>"
done
logsel="$logsel</select>"

cat<<-EOF
	<form name=sysutils action="/cgi-bin/sys_utils_proc.cgi" method="post">

	<fieldset><legend><strong>Reboot or Poweroff</strong></legend>
	<input type="submit" name="action" value="Reboot" onClick="return confirm('The box will reboot now.\nWithin 60 seconds you will be connected again.\n\nProceed?')">
	<input type="submit" name="action" value="Poweroff" onClick="return confirm('The box will poweroff now.\n\nProceed?')">
	</fieldset><br>

	<fieldset><legend><strong>View Logs</strong></legend>
	$logsel
	</fieldset><br>
	
	<fieldset><legend><strong>Services</strong></legend>
	<input type="submit" name="action" value="StartAll">
	<input type="submit" name="action" value="StopAll">
	<input type="submit" name="action" value="RestartAll">
	</fieldset><br>

	<fieldset><legend><strong>Administering password</strong></legend>
	Current Password:<input type="password" autocomplete="off" name="passwd" value="" onkeypress="return event.keyCode != 13">
	<input type="submit" name="action" value="ChangePassword">
	</fieldset><br>
EOF

if test -s /etc/printcap; then
	cat<<-EOF
		<fieldset><legend><strong>Printers</strong></legend>
		<input type=submit name="action" value="ClearPrintQueues">
		</fieldset><br>
	EOF
fi

cat<<-EOF
	<fieldset><legend><strong>SSL Certificate</strong></legend>
	<input type=submit name="action" value="createNew" $(ttip ssl_tt)>
	</fieldset><br>
	</form></body></html>
EOF

