#!/bin/sh

CONFM=/etc/misc.conf
THM_DIR=/usr/www/scripts

. common.sh
check_cookie

#write_header "System utilities" "document.sysutilsf.reset()"
write_header "System utilities"

mktt ssl_tt "Erases current SSL certificates and creates a new one.<br>
Needed when changing the host name or domain.<br>
WARNING: if using https your browser will complain<br>
and you will have to make it accept the new certificate.<br>
Does not affects the ssh host key."

mktt wday_tt "Week or Month day(s) to execute the command.<br><br><strong>Week day</strong>: 0-Sun, 1-Mon, 2-Tue...<br>0,2,4 means Sun, Tue and Thu<br>0-2 means Sun, Mon and Tue<br>* means everyday.<br><br><strong>Month day:</strong> first character must be a 'd',<br> 1 to 31 allowed, same rules as above applies,<br> e.g., 'd1,15' or 'd1-5' or 'd28' are valid.<br><br>No spaces allowed, no checks done"

mktt hour_tt "'Hour' or 'Hour:Minute' or ':Minute' of the day to execute the command, 0..23:0..59.<br><br>Use the same format for hour and minute as in the \"When\" field."

mktt next_tt "Next scheduled power up date and time,<br>YYYY-MM-DD and HH:MM, the year is ignored."

mktt rep_tt "Amount to add to reschedule the power up since the last one occurred.<br>\"+Nd\" for days or \"+Nm\" for months."

logsel="<select name=\"logaction\" onchange=\"return submit()\">
<option>Select one</option>
<option value=\"SystemConf\">System Configuration</option>
<option value=\"KernelLog\">Kernel Log</option>
<option value=\"SystemLog\">System Log</option>
<option value=\"Processes\">Running Processes</option>"

for i in $(find /var/log/ -name \*.log\* -o -name log.\* -o -name \*_log); do
	logsel="$logsel<option value=\"$i\">$(basename $i | sed -r 's/(\.log|log\.|_log)//g')</option>"
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

	<fieldset><legend>Power up, Power off, Reboot</legend>
	<table><tr><td colspan=3>
	<input type="submit" name="action" value="Reboot" onClick="return confirm('The box will reboot now.\nWithin 60 seconds you will be connected again.\n\nProceed?')">
	<input type="submit" name="action" value="RebootAndCheck" onClick="return confirm('The box will reboot now and perform a complete filesystem check, during which its data will not be available.\nWithin 60 seconds you will be connected again.\n\nProceed?')">
	<input type="submit" name="action" value="Poweroff" onClick="return confirm('The box will poweroff now.\n\nProceed?')">
	</td></tr>
EOF

if grep -qE 'DNS-320-Bx|DNS-320L-Ax|DNS327L-Ax' /tmp/board; then

	if test -n "$POWERUP_AFTER_POWER_FAIL"; then
		apr_chk="checked"
	fi

	if test -n "$POWERUP_ON_WOL"; then
		wol_chk="checked"
	fi
	#wol_chk="disabled"  #not working

	# scheduled power up
	res=$(dns320l-daemon -x readalarm)
	if ! echo "$res" | grep -q disabled; then
		spu_when=$(echo "$res" | awk '{printf("%s", $(NF-1))}')
		spu_at=$(echo "$res" | awk '{printf("%s", $NF)}')
	elif test -n "$POWERUP_ALARM_SET"; then
		spu_chk="checked"
		year=$(date +%Y)
		spu_when=$(echo $POWERUP_ALARM_SET | awk '{printf("'$year'-%d-%d", $1,$2)}')
		spu_at=$(echo $POWERUP_ALARM_SET | awk '{printf("%d:%d", $3,$4)}')
	else
		spu_when=$(date +%F)
		spu_at=$(date +%R)
	fi

	if test -n "$POWERUP_ALARM_REPEAT"; then
		spu_chk="checked"
		spu_rep=$POWERUP_ALARM_REPEAT
	else
		spu_rep="+1d"
	fi

	# scheduled power down
	TF=$(mktemp -t)
	if test -n "$POWERDOW_SET"; then
		echo "$POWERDOW_SET" > $TF
		read min hour monthday month weekday cmd < $TF
		if test "$monthday" != '*'; then
			weekday="d$monthday"
		fi
		spd_chk="checked"
		spd_wday=$weekday
		spd_at="$hour:$min"	
	else
		crontab -l > $TF 2> /dev/null
		while read min hour monthday month weekday cmd; do
			if ! echo "$cmd" | grep -q "/usr/sbin/poweroff"; then continue; fi

			if test "$monthday" != '*'; then
				weekday="d$monthday"
			fi
			spd_chk="checked"
			spd_wday=$weekday
			spd_at="$hour:$min"
			break
		done < $TF
	fi
	rm -f $TF

	if test -z "$min" -o -z "$hour" -o -z "$monthday" -o -z "$month" -o -z "$weekday"; then
		spd_at="0:0"; spd_wday="*"
	fi

cat<<-EOF
	<tr><td><br></td></tr>
	<tr>
	<td><input type=checkbox $apr_chk name=set_apr value=yes></td>
	<td colspan=3>Enable Automatic Power On after power failure</td>
	<td></td><td></td>
	</tr>
	<tr>
	<td><input type=checkbox $wol_chk name=set_wol value=yes></td>
	<td colspan=3>Enable Wake On Lan <em>(not properly working)</em></td>
	<td></td><td></td>
	</tr>
	<tr>
	<td><input type=checkbox $spd_chk name=set_spd value=yes></td>
	<td colspan=3>Enable Scheduled Power Down</td>
	<td></td><td></td>
	</tr>
	<tr>
	<td></td>
	<td>When:</td>
	<td><input type=text size=10 name=spd_wday value="$spd_wday" $(ttip wday_tt)> At: <input type=text size=10 name=spd_at value="$spd_at" $(ttip hour_tt)></td>
	<td></td>
	</tr>
	<tr>
	<td><input type=checkbox $spu_chk name=set_spu value=yes></td>
	<td colspan=3>Enable Scheduled Power Up</td>
	<td></td><td></td>
	</tr>
	<tr>
	<td></td>
	<td>Next:</td>
	<td><input type=text size=10 name=spu_when value="$spu_when" $(ttip next_tt)> At: <input type=text size=10 name=spu_at value="$spu_at" $(ttip next_tt)></td>
	</tr><tr>
	<td></td>
	<td>Repeat every:</td>
	<td><input type=text size=10 name=spu_rep value="$spu_rep" $(ttip rep_tt)></td>
	</tr><tr>
	<td colspan=2><input type="submit" name="action" value="Submit"></td>
	</tr>
EOF
fi

cat<<-EOF
	</table>
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
	Current Password:<input type="password" id="passwd_id" name="passwd" value="" onkeypress="return event.keyCode != 13">
	<input type="submit" name="action" value="ChangePassword" onclick="return csubmit()">
	<input type="hidden" id=salt_id name=salt value="$salt">
	</fieldset>
EOF

if test -s /etc/printcap; then
	cat<<-EOF
		<fieldset><legend>Printers</legend>
		<input type=submit name="action" value="ClearPrintQueues">
		</fieldset>
	EOF
fi

eval $(openssl x509 -in /etc/ssl/certs/server.pem -noout -subject | awk  -F '/' '{print $2,$3,$4}')

cat<<-EOF
	<fieldset><legend>Current SSL Certificate</legend>
Issued by <strong>$O</strong> for a <strong>$OU</strong> with <strong>$CN</strong> as hostname 
	<input type=submit name="action" value="createNew" $(ttip ssl_tt)>
	</fieldset>
	</form>
	<fieldset><legend>Theme</legend>
	<form id="sysutilsf2" name="sysutilsf2" action="/cgi-bin/sys_utils_proc.cgi" method="post">
	<select name="set_thm" onchange="document.sysutilsf2.theme.value='theme'; return submit()">$opt</select>
	<input type=submit name=action value="DeleteTheme">
	Disable top menu:<input $notop_chk type="checkbox" name="notop_menu" value="no" onchange="document.sysutilsf2.theme.value='theme'; return submit()">
	Disable side menu:<input $noside_chk type="checkbox" name="noside_menu" value="no" onchange="document.sysutilsf2.theme.value='theme'; return submit()">
	<input type="hidden" name="theme" value=""><br><br>
	</form>
	<form action="/cgi-bin/sys_utils_proc.cgi" method="post" enctype="multipart/form-data">
	Load theme from file: <input type=file name=theme.zip>
	<input type=submit name=action value="UploadTheme" onClick="return confirm('Uploading themes can make the webUI susceptible to exploitations and attacks.\n\nProceed?')"><br>
	</form>
	</fieldset>
	</body></html>
EOF

