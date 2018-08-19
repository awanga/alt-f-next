#!/bin/sh

# TZ setting:
# http://www.gnu.org/savannah-checkouts/gnu/libc/manual/html_node/TZ-Variable.html_node
# http://pubs.opengroup.org/onlinepubs/007904975/basedefs/xbd_chap08.html (near the end)
#
# timezones.txt was *crudely* extracted from /usr/share/zoneinfo/posix
# from SuSE package timezone-2009d-0.1.1.
# An alternative zonelist:
# http://uclibc.10924.n7.nabble.com/attachment/5058/0/uclibc-zoneinfo.list

# $1-default month
opt_month() {
	j=1
	for i in Jan Fev Mar Apr May Jun Jul Aug Sep Oct Nov Dec; do
		sel=""
		if test "$j" = "$1"; then
			sel="selected"
		fi
		echo "<option $sel value=\"$j\">$i</option>"
		j=$((j+1))
	done
}
	
opt_wday() {
	j=0
	for i in Sun Mon Tue Wed Thu Fri Sat; do
		sel=""
		if test "$j" = "$1"; then
			sel="selected"
		fi
		echo "<option $sel value=\"$j\">$i</option>"
		j=$((j+1))
	done
}

opt_week() {
	j=1
	for i in first 2nd 3d 4th last; do
		sel=""
		if test "$j" = "$1"; then
			sel="selected"
		fi
		echo "<option $sel value=\"$j\">$i</option>"
		j=$((j+1))
	done
}

opt_hour() {
	for i in $(seq 0 23); do
		sel=""
		if test "$i" = "$1"; then
			sel="selected"
		fi
		echo "<option $sel value=\"$i\">$i</option>"
	done
}

opt_min() {
	for i in $(seq 0 15 45); do
		sel=""
		if test "$i" = "$1"; then
			sel="selected"
		fi
		echo "<option $sel value=\"$i\">$i</option>"
	done
}

tzones() {

	echo "<select name=tz_opt onChange=\"update_tz()\">"

	while read city zone; do
		sel=""
		if test "$timezone" = "$city"; then
			sel="SELECTED"
			fnd=$zone
		fi
		echo "<option $sel value=\"$zone\"> $city </option>"
	done < timezones.txt

	if test -z "$fnd"; then
		echo "<option SELECTED value=\"\">Select one Continent/City</option>"
	fi

	echo "</select>"	
}

# not used
parse_tz() {
	eval $(echo "$tz" | awk -F ',' \
		'{printf "ptz=%s;dsts=%s;dste=%s", $1, $2, $3}')

	if test -n "$dsts"; then
		eval $(echo $dsts | tr 'M./:' ' '  | awk \
			'{printf "months=%s;weeks=%s;days=%s;hours=%s;mins=%s", \
				$1, $2, $3, $4, $5}')
		if test -z "$hours"; then hours=2; mins=0; fi

		eval $(echo $dste | tr 'M./:' ' '  | awk \
			'{printf "monthe=%s;weeke=%s;dayse=%s;houre=%s;mine=%s", \
				$1, $2, $3, $4, $5}')
		if test -z "$houre"; then houre=2; mine=0; fi
	fi
}

CONFT=/etc/timezone	# dont edit, use the web time setup interface!
CONFZ=/etc/TZ	# this is the real thing, if you known how, you can modify it
CONFNTP=/etc/ntp.conf

. common.sh
check_cookie
write_header "Time Setup"

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

ntps="0.pool.ntp.org"
if test -e $CONFNTP; then
	while read server host; do
		if test "$server" = "server" -a "$host" != "127.127.1.0"; then
			ntps=$host
			default_ntpd_server="<option value=\"$ntps\">Default</option>"
			break
		fi
	done < $CONFNTP
fi
 
parse_tz

#debug 

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
	function toogle() {
		st = document.getElementById("fixdst").checked
		for (i=1; i<11; i++)
			document.getElementById("fix" + i).disabled = ! st
	}
	</script>

<form name=frm action="/cgi-bin/time_proc.cgi" method="post">

<fieldset><legend>Country</legend>
<table>
	<tr><td>Timezone:</td><td><input type=text size=30 name=tz value="$tz">
	$(tzones)
	<input type=hidden name=timezone value="$timezone"></td></tr>

	<tr><td></td><td>Fix Daylight Saving Time (DST)
	<input type=checkbox id=fixdst name=fixdst value=po onclick="toogle()"></td></tr>

	<tr><td></td><td>DST start date
	<select disabled id=fix1 name=dst_week_start onChange="update_tz2()">
			$(opt_week $weeks)</select>

	<select disabled id=fix2 name=dst_day_start onChange="update_tz2()">
		$(opt_wday $days)</select>of

	<select disabled id=fix3 name=dst_mth_start onChange="update_tz2()">
		$(opt_month $months)</select>at

	<select disabled id=fix4 name=dst_hour_start onChange="update_tz2()">
		$(opt_hour $hours)</select>:

	<select disabled id=fix5 name=dst_min_start onChange="update_tz2()">
		$(opt_min $mins)</select></td></tr>

	<tr><td></td><td>DST &nbsp;end date
	<select disabled id=fix6 name=dst_week_end onChange="update_tz2()">
		$(opt_week $weeke)</select>

	<select disabled id=fix7 name=dst_day_end onChange="update_tz2()">
		$(opt_wday $daye)</select>of

	<select disabled id=fix8 name=dst_mth_end onChange="update_tz2()">
	$(opt_month $monthe)</select>at

	<select disabled id=fix9 name=dst_hour_end onChange="update_tz2()">
		$(opt_hour $houre)</select>:

	<select disabled id=fix10 name=dst_min_end onChange="update_tz2()">
		$(opt_min $mine)</select></td></tr>

<tr><td></td><td><input type="submit" name="country" value="Submit"></td></tr>
</table></fieldset>

<fieldset>
<legend>Adjust time through internet</legend>
<table>
	<tr><td>Local time:</td>
	<td colspan=2><input type=text size=30 READONLY value="$ltime"></td>
	</tr>

	<tr><td>Adjust from:</td>
		<td><input type=text size=20 name=ntps value="$ntps"></td>
		<td><select name=ntps_opt onChange="update_smtp()">
		$default_ntpd_server
		<option value="0.pool.ntp.org">Worldwide</option>
		<option value="africa.pool.ntp.org">Africa</option>
		<option value="asia.pool.ntp.org">Asia</option>
		<option value="europe.pool.ntp.org">Europe</option>
		<option value="north-america.pool.ntp.org">North America</option>
		<option value="oceania.pool.ntp.org">Oceania</option>
		<option value="south-america.pool.ntp.org">South America</option>
	</select></td>
	</tr>
	<tr><td></td><td><input type=submit name=ntpserver value="Submit"></td><td></td></tr>
</table>
</fieldset>

<fieldset>
<legend>Adjust time manually</legend>	
<table>	
	<tr><td>Set Hour:</td>
		<td><input type=text name=hour value="$hour"></td>
		<td>24H</td></tr>
	
	<tr><td>And Date:</td>
		<td><input type=text name=date value="$date"></td>
		<td>YYYY-MM-DD</td></tr>

	<tr><td></td><td><input type="submit" name="manual" value="Submit"></td>
	<td></td></tr>
</table>	
</fieldset>

</form></body></html>
EOF

