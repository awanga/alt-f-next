#!/bin/sh

. common.sh
check_cookie
write_header "Temperature, Fan and Buttons Setup"

CONFF=/etc/sysctrl.conf

if test -f $CONFF; then
	# why the hell did I do this this way???
	# while read  line; do
	#  eval $(echo $line | awk -F"=" '!/#/{if (NF == 2) printf "%s=%s\n",
	#  gensub(/ */,"","g", $1), gensub(/ */,"","g", $2)}')
	# done < $CONFF
	. $CONFF
else
	lo_fan=2000
	hi_fan=5000
	lo_temp=40
	hi_temp=50
	fan_off_temp=40
	max_fan_speed=5000
	warn_temp=52
	warn_temp_command=
	crit_temp=54
	crit_temp_command="/sbin/poweroff"
	front_button_command1=
	front_button_command2=
	back_button_command=
fi


cat<<-EOF
    <form action="/cgi-bin/sysctrl_proc.cgi" method="post">


    <fieldset><Legend><strong>System Temperature / Fan Speed relationship</strong>
      </legend><table>
        <tr><td>Low Temp. (C):</td>
          <td><input type=text size=4 name=lo_temp value=$lo_temp></td>
    	  <td>Low Fan Speed (RPM):</td>
          <td><input type=text size=4 name=lo_fan value="$lo_fan"></td>
        </tr>

        <tr><td>High Temp. (C):</td>
          <td><input type=text size=4 name=hi_temp value=$hi_temp></td>
    	  <td>High Fan Speed (RPM):</td>
          <td><input type=text size=4 name=hi_fan value="$hi_fan"></td>
        </tr>
      </table></fieldset>

    <fieldset><Legend><strong>Maximum ratings</strong>
      </legend><table>
        <tr><td>Fan Off Temp. (C):</td>
          <td><input type=text size=4 name=fan_off_temp value="$fan_off_temp">
	</td></tr>
      	<tr><td>Max Fan Speed (RPM)</td>
          <td><input type=text size=4 name=max_fan_speed value="$max_fan_speed"></td>
        </tr>
    </table></fieldset>

    <fieldset><Legend><strong>System Safety</strong>
      </legend><table>
        <tr><td>Warn Temp. (C):</td>
          <td><input type=text size=4 name=warn_temp value=$warn_temp></td>
          <td>Command to execute:</td>
	  <td><input type=text name=warn_temp_command 
		value="$warn_temp_command"></td>
        </tr>

        <tr><td>Critical Temp. (C):</td>
          <td><input type=text size=4 name=crit_temp value=$crit_temp></td>
          <td>Command to execute:</td>
	  <td><input type=text name=crit_temp_command 
		value="$crit_temp_command"></td>
        </tr>
    </table></fieldset>

    <fieldset><Legend><strong>Action to execute on Button press</strong>
      </legend><table>
        <tr><td>Front button 1st cmd:</td>
          <td COLSPAN=3><input type=text name=front_button_command1
		 value=$front_button_command1></td>
        </tr>

        <tr><td>Front button 2nd cmd:</td>
          <td COLSPAN=3><input type=text name=front_button_command2 
		value=$front_button_command2></td>
        </tr>

        <tr><td>Back button cmd:</td>
          <td COLSPAN=3><input type=text name=back_button_command 
		value=$back_button_command></td>
        </tr>
      </table></fieldset>

    <TR><TD><input type="submit" value="Submit"></TD>
	<td></td><td></td><td></td>
    </TR>
    </table></form></body></html>
EOF
