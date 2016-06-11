#!/bin/sh

. common.sh
check_cookie
write_header "Temperature, Fan and Buttons Setup"

CONFF=/etc/sysctrl.conf
CONFM=/etc/misc.conf

mktt tt_1cmd "User script to execute before the box reboots. Read the online help"
mktt tt_2cmd "User script to execute before the box powers-down. Read the online help"
mktt tt_3cmd "User script to execute when pressing the back button. Read the online help"
mktt fanoff_tt "The fan turns off at system temperatures lower than this value"
mktt hist_temp_tt "Temperature window around temperature change points"

board=$(cat /tmp/board)

# keep in sync with sysctrl.c, args_t args, line ~84
lo_fan=2000
hi_fan=5000
hi_temp=50
fan_mode=0
hist_temp=1
mail=1
recovery=1
fan_off_temp=38
max_fan_speed=6000
warn_temp=52
crit_temp=54
warn_temp_command=
crit_temp_command="/usr/sbin/poweroff"
front_button_command1=
front_button_command2=
back_button_command=

if test -f $CONFF; then
	. $CONFF
fi

if test "$recovery" = "1"; then
	recovchk=checked
fi

if test "$mail" = "1"; then
	mailchk=checked
fi

if test -e $CONFM; then
	SENDTO=$(awk -F= '/^MAILTO/{print $2}' $CONFM)
	if test -z "$SENDTO"; then NOMAILF=disabled; fi
fi

cat<<-EOF
	<script type="text/javascript">
		function tdis() {
			obj = document.getElementById("fanmode_id")
			idx = obj.selectedIndex
			st = false
			if (obj.options[idx].value != 0)
				st = true
			document.getElementById("fanoff_id").disabled = st
			document.getElementById("lotemp_id").disabled = st
			document.getElementById("histtemp_id").disabled = st
		}
	</script>
	<form action="/cgi-bin/sysctrl_proc.cgi" method="post">
	<fieldset><legend>System Temperature / Fan Speed relationship</legend><table>
EOF

case "$board" in
	DNS-323-[AB]1)

	if test -z "$lo_temp"; then lo_temp=40; fi

	cat<<-EOF
		<tr><td>Low Temp.</td>
			<td><input type=text size=2 name=lo_temp value="$lo_temp">&deg;C</td>
			<td width=20></td>
			<td>Low Fan Speed</td>
			<td><input type=text size=4 name=lo_fan value="$lo_fan">RPM</td>
		</tr>
		<tr><td>High Temp.</td>
			<td><input type=text size=2 name=hi_temp value="$hi_temp">&deg;C</td>
			<td></td>
			<td>High Fan Speed </td>
			<td><input type=text size=4 name=hi_fan value="$hi_fan">RPM</td>
		</tr>
		</table></fieldset>

	<fieldset><legend>Maximum ratings</legend><table>
			<tr><td>Fan Off Temp.</td>
				<td><input type=text size=2 name=fan_off_temp value="$fan_off_temp" $(ttip fanoff_tt)>&deg;C
				</td></tr>
			<tr><td>Temp. hysteresis</td>
				<td><input type=text size=2 name=hist_temp value="$hist_temp" $(ttip hist_temp_tt)>&deg;C
				</td></tr>
			<tr><td>Max Fan Speed </td>
				<td><input type=text size=4 name=max_fan_speed value="$max_fan_speed">RPM</td>
			</tr>
		</table></fieldset>
	EOF
	;;

	DNS-320-[AB]x|DNS-320L-Ax|DNS-321-Ax|DNS-323-C1|DNS-325-Ax|DNS-327L-Ax)

	mktt lofan_tt "The fan turns at low speed at system temperatures lower than this value<br> and at fast speed at higher temperatures"
	if test -z "$lo_temp"; then lo_temp=45; fi

	fmode="<select name=fan_mode id=fanmode_id onChange=\"tdis()\">"

	i=0
	for mode in "Auto" "Always Off" "Always Low" "Always Fast"; do
		sel=""; if test "$fan_mode" = $i; then sel="selected"; fi
		fmode="${fmode}<option $sel value=$i>$mode</option>"
		i=$((++i))
	done
	fmode="${fmode}</select>"

	cat<<-EOF
		<tr><td>Fan mode</td><td>$fmode</td></tr>
		<tr><td>Fan Off Temp.</td>
			<td><input type=text size=2 id=fanoff_id name=fan_off_temp value="$fan_off_temp" $(ttip fanoff_tt)>&deg;C
			</td></tr>
		<tr><td>Low Fan Speed Temp.</td>
			<td><input $temp_dis type=text size=2 id=lotemp_id name=lo_temp value="$lo_temp" $(ttip lofan_tt)>&deg;C</td></tr>
		<tr><td>Temp. hysteresis</td>
			<td><input $temp_dis type=text size=2 name=hist_temp id=histtemp_id value="$hist_temp" $(ttip hist_temp_tt)>&deg;C</td></tr>
		</table></fieldset>
	EOF
	;;
	
	*)
	echo "Unknown board $board</table></fieldset>"
	;;
esac

if test "$board" = "DNS-320L-Ax" -o "$board" = "DNS-320-Bx"; then fb_dis="disabled"; fi

cat<<-EOF
	<fieldset><legend>System Safety</legend><table>
			<tr><td>Warn Temp. </td>
				<td><input type=text size=4 name=warn_temp value="$warn_temp">&deg;C</td>
				<td width=20></td>
				<td>Command to execute:</td>
				<td><input type=text name=warn_temp_command value="$warn_temp_command"></td>
			</tr>
			<tr><td>Critical Temp.</td>
				<td><input type=text size=4 name=crit_temp value="$crit_temp">&deg;C</td>
				<td></td>	
				<td>Command to execute:</td>
				<td><input type=text name=crit_temp_command value="$crit_temp_command"></td>
			</tr>
			<tr><td>Send email</td>
				<td><input type=checkbox $mailchk name=mail value="1"></td>
				<td></td>
				<td>Send mail to</td>
				<td><input type=text readonly name=sendto value="$SENDTO">
				Use "Setup Mail" to change</td>
			</tr>
		</table></fieldset>

	<fieldset><legend>Action to execute on Button press</legend><table>
			<tr><td>Front button 1st cmd:</td>
				<td colspan=3><input $fb_dis type=text name=front_button_command1  value="$front_button_command1" $(ttip tt_1cmd)></td>
			</tr>
			<tr><td>Front button 2nd cmd:</td>
				<td colspan=3><input $fb_dis type=text name=front_button_command2 value="$front_button_command2" $(ttip tt_2cmd)></td>
			</tr>
			<tr><td>Back button cmd:</td>
				<td colspan=3><input type=text name=back_button_command value="$back_button_command" $(ttip tt_3cmd)></td>
			</tr>
			<tr><td>Enable Recovery</td>
				<td><input type=checkbox $recovchk name=recovery value="1"></td>
			</tr>
		</table></fieldset>

	<p><input type="submit" value="Submit">	$(back_button)
	</form>
	<script type="text/javascript">
	tdis()
	</script>
	</body></html>
EOF
