#!/bin/sh

. common.sh

check_cookie
write_header "Disk Utilities"

CONFT=/etc/misc.conf
CONFB=/etc/bay

dstatus() {
	local res dsk
	dsk=$1
	
	if test -b /dev/$dsk; then
		res=$(hdparm -C /dev/$dsk | awk '/drive/{print $4}') >/dev/null 2>&1
	else
		res="None"
	fi
	echo $res
}

has_disks

. /tmp/power_mode

if test -f $CONFT; then
	. $CONFT
fi
for i in HDSLEEP_LEFT HDSLEEP_RIGHT HDSLEEP_USB; do
	if test -z "$(eval echo \$$i)"; then
		eval $(echo $i=20)
	fi
done

cat<<EOF
	<script type="text/javascript">
	function submit() {
			document.getElementById("diskf").submit;
	}
	</script>

	<form id=diskf action="/cgi-bin/diskutil_proc.cgi" method="post">
	<fieldset><Legend><strong> Disks </strong></legend>
	<table>
	<tr align=center><th>Bay</th>
	<th>Dev.</th>
	<th>Disk Model</th>
	<th></th>
	<th>Health</th>
	<th>Power Mode</th>
	<th columnspan=2>Set Standby</th> 
EOF

while read ln; do
	if test -z "$ln"; then continue; fi
	eval $(echo $ln | awk '{
		printf "bay=%s;dsk=%s;hdtimeout=HDSLEEP_%s", $1, $2, toupper($1)}')
	stat=$(dstatus $dsk)
	paction="StandbyNow"
	if test "$stat" != "active/idle"; then
		paction="WakeupNow"
	fi
	mod=$(cat /sys/block/$dsk/device/model)
	val=$(eval echo \$$hdtimeout)
 
	echo "<tr><td>$bay</td><td>$dsk</td><td> $mod </td>"

	if ! test -b "/dev/$dsk"; then
		echo "<td></td><td></td><td></td><td></td>"
	else
		if eject -s $dsk > /dev/null; then
			ejectop="Load"
		else
			ejectop="Eject"
		fi
		cat<<-EOF	 
			<td> <input type="submit" name="$dsk" value="$ejectop"> </td>
			<td><select name="$dsk" onChange=submit()>
				<option value="">Select Action</option>
				<option value="hstatus">Show Status</option>
				<option value="shorttest">Start short test</option>
				<option value="longtest">Start long test</option>
			</select></td>
			<td> <input type="submit" name="$dsk" value="$paction"> </td>
		EOF
	fi

	echo "<td><input type="text" size=2 name="$hdtimeout" value="$val"> min.</td></tr>"
done < $CONFB

cat<<-EOF
	<tr>
	<td colspan=6></td>
	<td><input type="submit" name="standby" value="Submit"> </td>
	</tr>        
	</table>
	</fieldset><br>
	</form></body></html>
EOF
