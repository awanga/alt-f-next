#!/bin/sh

opt_month() {
	j=1
	for i in Jan Fev Mar Apr May Jun Jul Aug Sep Oct Nov Dec; do
		echo "<option value=$j>$i</option>"
		j=$((j+1))
	done
}
	
opt_wday() {
	j=0
	for i in Sun Mon Tue Wed Thu Fri Sat; do
		echo "<option value=$j>$i</option>"
		j=$((j+1))
	done
}

opt_week() {
	j=1
	for i in first 2nd 3d 4th last; do
		echo "<option value=$j>$i</option>"
		j=$((j+1))
	done
}

opt_hour() {
	for i in $(seq 0 23); do
		echo "<option value=$i>$i</option>"
	done
}

opt_min() {
	for i in $(seq 0 15 45); do
		echo "<option value=$i>$i</option>"
	done
}

# timezones.txt was *crudely* extracted from /usr/share/zoneinfo/posix
# from SuSE package timezone-2009d-0.1.1

tzones() {

	echo "<select name=tz_opt onChange='update_tz()'>"

# using <optgroup> this way is toooo sloow
#	lcontinent=""
#	echo "<optgroup label=Africa>"

	while read city zone; do
		sel=""
		if test "$timezone" = "$city"; then
			sel="SELECTED"
			fnd=$zone
		fi
#		continent=$(echo $city | cut -d'/' -f1)
#		if test "$lcontinent" != $continent; then
#			lcontinent=$continent
#			echo "</optgroup><optgroup label=$continent>"
#		fi
		echo "<option $sel value='$zone'> $city </option>"
	done < timezones.txt

	if test -z "$fnd"; then
		echo '<option SELECTED value="">Select one Continent/City</option>'
	fi

	echo "</select>"	
}

# not used
parse_tz() {
	eval $(echo "$tz" | awk -F ',' \
		'{printf "tz=%s;dsts=%s;dste=%s", $1, $2, $3}')

	if test -n "$dsts"; then
		eval $(echo $dsts | tr 'M./:' ' '  | awk \
			'{printf "months=%s;weeks=%s;days=%s;hours=%s;mins=%s", \
				$1, $2, $3, $4, $5}')
		if test -z "$hours"; then hours=2;mins=0; fi

		eval $(echo $dste | tr 'M./:' ' '  | awk \
			'{printf "monthe=%s;weeke=%s;dayse=%s;houre=%s;mine=%s", \
				$1, $2, $3, $4, $5}')
		if test -z "$houre"; then houre=2;mine=0; fi
	fi
}

CONFT=/etc/timezone	# dont edit, use the web time setup interface!
CONFZ=/etc/TZ	# this is the real thing, if you known how, you can modify it
CONFNTP=/etc/ntp.conf

. common.sh
check_cookie
write_header "Time Setup"

if test -f /tmp/firstboot; then
	cat<<-EOF
		<center>
		<h3>Welcome to your first login to Alt-F</h3>
		<h4>To continue setting up Alt-F, you should now specify where
		 you live, Submit  it,</h4>
		<h4> and then adjust the local time and date.</h4>
		</center>
	EOF
fi

if test -r $CONFZ; then
    tz=$(cat $CONFZ)
else
    tz=UTC
fi

if test -r $CONFT; then
	read timezone < $CONFT
fi

ltime="$(TZ=$tz date)"
hour=$(date +%R)
date=$(date +%F)

ntps="pool.ntp.org"
if test -e $CONFNTP; then
	while read server host; do
		if test "$server" = "server" -a "$host" != "127.127.1.0"; then
			ntps=$host
			default_ntpd_server="<option value=$ntps>Default</option>"
			break
		fi
	done < $CONFNTP
fi
 

cat<<-EOF
	<script type="text/javascript">
	function update_smtp() {
		document.frm.ntps.value = document.frm.ntps_opt.value;
	}
	function update_tz() {
		document.frm.tz.value = document.frm.tz_opt.value;
		document.frm.timezone.value = \
		document.frm.tz_opt.options[document.frm.tz_opt.selectedIndex].text;
	}
	function update_tz2() {
		// FIXME at start (interlock with update_tz() above)
		// should read the current dst date/time
		// from document.frm.tz_opt.value and 
		// update the dst date/time selectors accordingly
		ttz = String(document.frm.tz_opt.value);
		end = ttz.indexOf(",");
		if (end != -1) 
			ttz = ttz.slice(0, end);
		document.frm.tz.value = ttz + ",M" + 
		document.frm.dst_mth_start.value + "." +
		document.frm.dst_week_start.value + "." +
		document.frm.dst_day_start.value + "/" + 
		document.frm.dst_hour_start.value + ":" +
		document.frm.dst_min_start.value + ",M" +
		document.frm.dst_mth_end.value + "." +
		document.frm.dst_week_end.value + "." +
		document.frm.dst_day_end.value + "/" + 
		document.frm.dst_hour_end.value + ":" +
		document.frm.dst_min_end.value;
	}
	function toogle(theform) {
		for (var i = 0; i < theform.length; i++) {
			if (theform.elements[i].id == "dst")
				theform.elements[i].disabled = theform.elements[i].disabled ? false : true;
		}
	}
	</script>

    <form name=frm action="/cgi-bin/time_proc.cgi" method="post">

	<fieldset>
	<legend><strong>Country</strong></legend>
	<table>    
    <tr><td>Timezone:</td>
        <td><input type=text size=30 name=tz value=$tz></td>
        <td>$(tzones)</td>
        <td><input type=hidden name=timezone value=$timezone></td>
        <!--TD><a href="http://www.sonoracomm.com/support/20-voice-support/107-uclibc-tz">Some examples</TD-->
    </tr>

    <tr><td></td><td>Daylight Saving Time (DST)</td>
	<td><input type=checkbox name=po value=po onclick="toogle(frm)"></td>
	</tr>

	<tr><td></td>
	<td>DST start date</td>

	<td><select disabled id=dst name=dst_week_start onChange=update_tz2()>
	$(opt_week)</select>
	
	<select disabled id=dst name=dst_day_start onChange=update_tz2()>
	$(opt_wday)</select>

	of <select disabled id=dst name=dst_mth_start onChange=update_tz2()>
	$(opt_month)</select>

	at <select disabled id=dst name=dst_hour_start onChange=update_tz2()>
	$(opt_hour)</select>

	:<select disabled id=dst name=dst_min_start onChange=update_tz2()>
	$(opt_min)</select></td></tr>

	<tr><td></td><td>DST end date</td>
	
	<td><select disabled id=dst name=dst_week_end onChange=update_tz2()>
	$(opt_week)</select>

	<select disabled id=dst name=dst_day_end onChange=update_tz2()>
	$(opt_wday)</select>

	of <select disabled id=dst name=dst_mth_end onChange=update_tz2()>
	$(opt_month)</select>

	at <select disabled id=dst name=dst_hour_end onChange=update_tz2()>
	$(opt_hour)</select>

	:<select disabled id=dst name=dst_min_end onChange=update_tz2()>
	$(opt_min)</select></td></tr>

	<TR><TD></td><td><input type="submit" name="country" value="Submit"></TD>
	<td></td></TR>
	</table></fieldset><br>

<fieldset>
<legend><strong>Adjust time through internet</strong></legend>
<table>
    <tr><td>Local time:</td>
	<td colspan=2><input type=text size=30 READONLY value="$ltime"></td>
    </tr>

    <tr><td>Adjust from:</td>
        <td><input type=text size=20 name=ntps value=$ntps></td>
        <td><select name=ntps_opt onChange="update_smtp()">
		$default_ntpd_server
		<option value=pool.ntp.org>Worldwide</option>
		<option value=asia.pool.ntp.org>Asia</option>
		<option value=europe.pool.ntp.org>Europe</option>
		<option value=north-america.pool.ntp.org>North America</option>
		<option value=oceania.pool.ntp.org>Oceania</option>
		<option value=south-america.pool.ntp.org>South America</option>
	</select></td>
    </tr>
    <tr><td></td><td><input type=submit name=ntpserver value=Submit></td><td></td></tr>
</table>
</fieldset><br>

<fieldset>
<legend><strong>Adjust time manually</strong></legend>    
<table>    
    <tr><td>Set Hour:</td>
    	<td><input type=text name=hour value="$hour"></td>
	<td>24H</td></tr>
    
    <tr><td>And Date:</td>
	<td><input type=text name=date value="$date"></td>
	<td>YYYY-MM-DD</td></tr>

    <TR><TD></td><td><input type="submit" name="manual" value="Submit"></TD>
	<td></td></TR>
</table>	
</fieldset>

    </form>        
    </body>
    </html>
EOF

