#!/bin/sh

. common.sh
check_cookie
write_header "Temperature, Fan and Buttons Setup"

CONFF=/etc/sysctrl.conf
CONFM=/etc/msmtprc

board="$(cat /tmp/board)"

# keep in sync with sysctrl.c, args_t args, line ~84
lo_fan=2000
hi_fan=5000
if test "$board" = "C1"; then 
	lo_temp=45
else
	lo_temp=40
fi
hi_temp=50
mail=1
recovery=1
fan_off_temp=38
max_fan_speed=5500
warn_temp=52
crit_temp=54
warn_temp_command=
crit_temp_command="/sbin/poweroff"
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
	SENDTO=$(awk '/^from/{ print $2}' $CONFM)
	if test -z "$SENDTO"; then NOMAILF=disabled; fi
fi

cat<<-EOF
	<form action="/cgi-bin/sysctrl_proc.cgi" method="post">

	<fieldset><Legend><strong>System Temperature / Fan Speed relationship</strong>
		</legend><table>
EOF


mktt fanoff_tt "The fan turns off at system temperatures lower than this value"

if test "$board" = "C1"; then
	mktt lofan_tt "The fan turns at low speed at system temperatures lower than this value<br> and at fast speed at higher temperatures"
	cat<<-EOF
			<tr><td>Fan Off Temp. (C):</td>
				<td><input type=text size=4 name=fan_off_temp value="$fan_off_temp" $(ttip fanoff_tt)>
				</td></tr>

			<tr><td>Low Fan Speed Temp. (C):</td>
				<td><input type=text size=4 name=lo_temp value="$lo_temp" $(ttip lofan_tt)></td>
		</table></fieldset><br>
	EOF
else 
	cat<<-EOF
			<tr><td>Low Temp. (C):</td>
				<td><input type=text size=4 name=lo_temp value="$lo_temp"></td>
				<td>Low Fan Speed (RPM):</td>
				<td><input type=text size=4 name=lo_fan value="$lo_fan"></td>
			</tr>
			<tr><td>High Temp. (C):</td>
				<td><input type=text size=4 name=hi_temp value="$hi_temp"></td>
				<td>High Fan Speed (RPM):</td>
				<td><input type=text size=4 name=hi_fan value="$hi_fan"></td>
			</tr>
		</table></fieldset><br>

	<fieldset><Legend><strong>Maximum ratings</strong>
		</legend><table>
			<tr><td>Fan Off Temp. (C):</td>
				<td><input type=text size=4 name=fan_off_temp value="$fan_off_temp"  $(ttip fanoff_tt)>
				</td></tr>
			<tr><td>Max Fan Speed (RPM)</td>
				<td><input type=text size=4 name=max_fan_speed value="$max_fan_speed"></td>
			</tr>
		</table></fieldset><br>
	EOF
fi

cat<<-EOF
	<fieldset><Legend><strong>System Safety</strong>
		</legend><table>
			<tr><td>Warn Temp. (C):</td>
				<td><input type=text size=4 name=warn_temp value="$warn_temp"></td>
				<td>Command to execute:</td>
				<td><input type=text name=warn_temp_command value="$warn_temp_command"></td>
			</tr>
			<tr><td>Critical Temp. (C):</td>
				<td><input type=text size=4 name=crit_temp value="$crit_temp"></td>
				<td>Command to execute:</td>
				<td><input type=text name=crit_temp_command value="$crit_temp_command"></td>
			</tr>
			<tr><td>Send email</td>
				<td><input type=checkbox $mailchk name=mail value="1"></td>
				<td>Send mail to </td>
				<td><input type=text readonly name=sendto value="$SENDTO"></td>
				<td>Use "Mail Setting" to change</td>
			</tr>
		</table></fieldset><br>

	<fieldset><Legend><strong>Action to execute on Button press</strong>
		</legend><table>
			<tr><td>Front button 1st cmd:</td>
				<td colspan=3><input type=text name=front_button_command1  value="$front_button_command1"></td>
			</tr>
			<tr><td>Front button 2nd cmd:</td>
				<td colspan=3><input type=text name=front_button_command2 value="$front_button_command2"></td>
			</tr>
			<tr><td>Back button cmd:</td>
				<td colspan=3><input type=text name=back_button_command value="$back_button_command"></td>
			</tr>
			<tr><td>Enable Recovery</td>
				<td><input type=checkbox $recovchk name=recovery value="1"></td>
			</tr>
		</table></fieldset><br>

	<table><tr><td><input type="submit" value="Submit">	$(back_button)</td>
		<td></td><td></td><td></td></tr>
		</table></form></body></html>
EOF
