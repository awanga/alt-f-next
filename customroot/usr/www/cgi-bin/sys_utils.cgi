#!/bin/sh

CONFM=/etc/misc.conf
THM_DIR=/usr/www/scripts

. common.sh
check_cookie

#write_header "System utilities" "document.sysutilsf.reset()"
write_header "System utilities"

mktt ssl_tt "Erases current SSL certificates and creates a new one.<br>
Needed when changing the host name.<br>
WARNING: your browser will complain and you will have to delete<br>
or revoke the old certificate and make the browser accept the new one.<br>
Does not affects the ssh host key."

logsel="<select name=\"logaction\" onchange=\"return submit()\">
<option>Select one</option>
<option value=\"SystemConf\">System Configuration</option>
<option value=\"KernelLog\">Kernel Log</option>
<option value=\"SystemLog\">System Log</option>
<option value=\"Processes\">Running Processes</option>"

for i in $(find /var/log/ -name \*.log\* -o -name log.\* -o -name \*_log); do
	logsel="$logsel<option value=$i>$(basename $i | sed -r 's/(\.log|log\.|_log)//g')</option>"
done
logsel="$logsel</select>"

fixlst=$(fixup list | while read st fx; do
	chk="&nbsp;"
	if test "$st" = "0"; then chk="&#x2713;"; fi
	fxi=$(echo $fx | cut -d"-" -f1)
	echo "<option value=\"$fxi\">$chk $fx</option>"
done)

fixsel="<select name=\"fixaction\">
<option>Select one</option>$fixlst</select>"

if test -f $CONFM; then
	. $CONFM
fi

if test "$TOP_MENU" = "no"; then notop_chk="checked"; fi
if test "$SIDE_MENU" = "no"; then noside_chk="checked"; fi

def_thm=$(basename $(readlink -f $THM_DIR/default.thm))
for i in $THM_DIR/*.thm; do
	if ! test -h $i; then
		thm=$(basename $i)
		sel=""; if test "$thm" = "$def_thm"; then sel="selected"; fi
		opt="$opt <option $sel value=\"$thm\">$(basename $thm .thm): $(sed -n '/^#/s/^#[[:space:]]*//p' $i)</option>"
	fi
done

salt=$(uuidgen)
echo -n $salt > /tmp/salt

md5 # expand js md5()

cat<<-EOF
	<script type="text/javascript">
	function csubmit() {
		obj = document.getElementById('passwd_id')
		obj.value = md5(obj.value + document.getElementById('salt_id').value)
		return true
	}
	</script>
	<form id="sysutilsf" name="sysutilsf" action="/cgi-bin/sys_utils_proc.cgi" method="post">

	<fieldset><legend>Reboot or Poweroff</legend>
	<input type="submit" name="action" value="Reboot" onClick="return confirm('The box will reboot now.\nWithin 60 seconds you will be connected again.\n\nProceed?')">
	<input type="submit" name="action" value="RebootAndCheck" onClick="return confirm('The box will reboot now and perform a complete filesystem check, during which its data will not be available.\nWithin 60 seconds you will be connected again.\n\nProceed?')">
	<input type="submit" name="action" value="Poweroff" onClick="return confirm('The box will poweroff now.\n\nProceed?')">
	</fieldset>

	<fieldset><legend>View Logs</legend>
	$logsel
	</fieldset>
	
	<fieldset><legend>Services</legend>
	<input type="submit" name="action" value="StartAll">
	<input type="submit" name="action" value="StopAll">
	<input type="submit" name="action" value="RestartAll">
	</fieldset>

	<fieldset><legend>Fixes</legend>
	$fixsel
	<input type="submit" name="action" value="UpdateList">
	<input type="submit" name="action" value="Details">
	<input type="submit" name="action" value="Apply">
	<input type="submit" name="action" value="Rollback">
	<input type="submit" name="action" value="RemoveAll">
	</fieldset>

	<fieldset><legend>Administering password</legend>
	Current Password:<input type="password" autocomplete="off" id="passwd_id" name="passwd" value="" onkeypress="return event.keyCode != 13">
	<input type="submit" name="action" value="ChangePassword" onclick="return csubmit()">
	<input type="hidden" id=salt_id name=salt value="$salt">
	</fieldset>

	<fieldset><legend>Theme</legend>
	<select name="set_thm" onchange="document.sysutilsf.theme.value='theme'; return submit()">$opt</select>
	Disable top menu:<input $notop_chk type="checkbox" name="notop_menu" value="no" onchange="document.sysutilsf.theme.value='theme'; return submit()">
	Disable side menu:<input $noside_chk type="checkbox" name="noside_menu" value="no" onchange="document.sysutilsf.theme.value='theme'; return submit()">
	<input type="hidden" name="theme" value="">
	</fieldset>
EOF

if test -s /etc/printcap; then
	cat<<-EOF
		<fieldset><legend>Printers</legend>
		<input type=submit name="action" value="ClearPrintQueues">
		</fieldset>
	EOF
fi

cat<<-EOF
	<fieldset><legend>SSL Certificate</legend>
	<input type=submit name="action" value="createNew" $(ttip ssl_tt)>
	</fieldset>
	</form></body></html>
EOF

