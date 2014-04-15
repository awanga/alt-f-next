#!/bin/sh

. common.sh

check_cookie
write_header "Disk Utilities" "document.disku.reset()"

CONFT=/etc/misc.conf

mktt power_tt "Advanced Power Management<br>
(If grayed disk does not supported APM)<br> 
Higher power savings, lower performance, can spindown<br>
Medium power savings and performance, can spindown<br>
Low power saving, higher performance, can't spindown."

mktt spindown_tt "After this minutes of inactivity the disk will spin down,<br>
depending on the Power Saving Settings"

has_disks

if test -f $CONFT; then
	. $CONFT
fi
for i in HDSLEEP_LEFT HDSLEEP_RIGHT HDSLEEP_USB HDPOWER_LEFT HDPOWER_RIGHT; do
	if test -z "$(eval echo \$$i)"; then
		eval $(echo $i=0)
	fi
done

cat<<EOF
	<script type="text/javascript">
	function submit() {
			document.getElementById("diskf").submit;
	}
	</script>

	<form id=disku name=disku action="/cgi-bin/diskutil_proc.cgi" method="post">
	<fieldset>
	<legend>Disks</legend>
	<table>
	<tr><th>Bay</th>
	<th>Dev.</th>
	<th>Capacity</th>
	<th>Disk Model</th>
	<th></th>
	<th>Health</th>
	<th>Power Mode</th>
	<th>Power Sav.</th>
	<th class="highcol">Spindown</th> 
EOF

for disk in $disks; do
	dsk=$(basename $disk)
	disk_details $dsk

	power_dis="disabled"; hdtimeout_dis=""
	if hdparm -I $disk 2> /dev/null | grep -q "Adv. Power Management"; then
		power_dis=""
		hdtimeout_dis="disabled"
	fi

	stat=$(disk_power $dsk)
	paction="StandbyNow"
	paction_dis=""
	if test "$stat" = "standby"; then
		paction="WakeupNow"
	elif test "$stat" = "unknown"; then
		paction="Unknown"
		paction_dis="disabled"
	fi

	ejectop="Eject"
	if eject -s $dsk > /dev/null; then
		ejectop="Load"
	fi

	eval $(echo $dbay | awk '{
		printf "hdtimeout=HDSLEEP_%s; hdtimeout_val=$HDSLEEP_%s; power=HDPOWER_%s; power_val=$HDPOWER_%s", toupper($1), toupper($1), toupper($1), toupper($1)}')

	medpower_sel=""; highpower_sel=""; lowpower_sel=""; dispower_sel=""
	case $power_val in
		1) highpower_sel="selected" ;;
		127) medpower_sel="selected" ;;
		254) lowpower_sel="selected" ;;
		0|255) dispower_sel="selected"; hdtimeout_dis="" ;;
	esac
	
	cat<<-EOF	 
		<tr><td>$dbay</td><td>$dsk</td><td>$dcap</td><td>$dmod</td>
		<td><input type="submit" name="$dsk" value="$ejectop"></td>
		<td><select name="$dsk" onChange="return submit()">
			<option value="">Select Action</option>
			<option value="hstatus">Show Status</option>
			<option value="shorttest">Start short test</option>
			<option value="longtest">Start long test</option>
			</select></td>
		<td> <input type="submit" $paction_dis name="$dsk" value="$paction"> </td>
		<td><select $power_dis name=$power onchange="return submit()" $(ttip power_tt)>
			<option $dispower_sel value=255>Disable</option>
			<option $highpower_sel value=1>High</option>
			<option $medpower_sel value=127>Medium</option>
			<option $lowpower_sel value=254>Low</option>
			</select></td>
		<td class="highcol"><input type="text" size=2 $hdtimeout_dis name="$hdtimeout" value="$hdtimeout_val" $(ttip spindown_tt)> min.</td></tr>
	EOF
done

usb_swap_val="Enable"
if test "$USB_SWAP" = "yes"; then
	usb_swap_val="Disable"
fi

cat<<-EOF
	<tr><td colspan=8></td>
	<td class="highcol"><input type="submit" name="standby" value="Submit"></td></tr>
	</table>
	</fieldset>     
	<p>Swapping on USB devices: <input type="submit" name=usb_swap value="$usb_swap_val">
	</form></body></html>
EOF
