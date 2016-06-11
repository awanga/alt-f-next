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

mktt swap_tt "Non RAID Disk Swap Priority:<br>
If grayed disk doesn't has a swap partition.<br>
High priority makes disk swap area to be used before low priority disks swap area.<br>
With equal priorities disk swap areas will be equaly used, faster.<br>
None disables swap on that disk."

mktt usb_swap_tt "Swapping on USB flash pens is disabled by default, as it might shorten the pen life."

mktt swappiness_tt "Swappiness specifies how aggressively swap is used,<br>
with 0 almost disabling it and 100 actively using it."

mktt recreate_swap_tt "Creates and activates swap on all partitions of type swap.<br>
RAID1 based swap will be removed."

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
	function msubmit(action) {
		document.getElementById("action_id").value = action;
		document.getElementById("disku").submit();
	}
	</script>

	<form id=disku name=disku action="/cgi-bin/diskutil_proc.cgi" method="post">
	<input type="submit" style="display:none"><!--dummy *first* default submit!-->
	<input type="hidden" name="action" id="action_id" value="">
	<input type="hidden" name="count" value="$ndisks">
	<fieldset>
	<legend>Disks</legend>
	<table>
	<tr><th>Bay</th>
	<th>Dev.</th>
	<th>Capacity</th>
	<th>Disk Model</th>
	<th></th>
	<th>Health</th>
	<th>Swap Pri.</th>
	<th>Power Mode</th>
	<th>Power Sav.</th>
	<th class="highcol">Spindown</th> 
EOF

cnt=0
for disk in $disks; do
	cnt=$((++cnt))
	dsk=$(basename $disk)
	disk_details $dsk

	swap_dev=""; swap_pri=""; swap_dis=""; swap_none=""; swap_low=""; swap_med=""; swap_high=""
	eval $(awk '/\/dev\/'$dsk'/{printf "swap_dev=%s swap_pri=%d\n", substr($1,6), $5}' /proc/swaps)
	case $swap_pri in
		1) swap_low="selected" ;;
		2) swap_med="selected" ;;
		3) swap_high="selected" ;;
		*) swap_none="selected" ;;
	esac
	if test -z $swap_dev; then
		swap_dev=$(blkid -t TYPE=swap | awk '/\/dev\/'$dsk'/{print substr($1,6,4)}')
		if test -z $swap_dev; then
			swap_dev=$(sgdisk -p /dev/$dsk 2>/dev/null | awk '/swap/{printf "'$dsk'%d",$1}')
			if test -z $swap_dev; then swap_dis="disabled"; fi
		fi
	fi

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
		<td><input type="submit" name="$dsk" value="$ejectop" onClick="return msubmit('load_eject_act')"></td>
		<td><select name="$dsk" onChange="return msubmit('smart_act')">
			<option value="">Select Action</option>
			<option value="hstatus">Show Status</option>
			<option value="shorttest">Start short test</option>
			<option value="longtest">Start long test</option>
			</select></td>
		<td><input type="hidden" name="swapd_$cnt" value="$swap_dev">
			<select $swap_dis name="swapp_$cnt" onChange="return msubmit('swap_act')" $(ttip swap_tt)>
			<option $swap_none value="0">None</option>
			<option $swap_low value="1">Low</option>
			<option $swap_med value="2">Medium</option>
			<option $swap_high value="3">High</option>
			</select></td>
		<td><input type="submit" $paction_dis name="$dsk" value="$paction" onClick="return msubmit('wake_standby_act')"></td>
		<td><select $power_dis name="$power" onChange="return msubmit('power_act')" $(ttip power_tt)>
			<option $dispower_sel value=255>Disable</option>
			<option $highpower_sel value=1>High</option>
			<option $medpower_sel value=127>Medium</option>
			<option $lowpower_sel value=254>Low</option>
			</select></td>
		<td class="highcol"><input type="text" size=2 $hdtimeout_dis name="$hdtimeout" value="$hdtimeout_val" onkeypress="return event.keyCode != 13" $(ttip spindown_tt)> min.</td></tr>
	EOF
done

usb_swap_val="Enable"
if test "$USB_SWAP" = "yes"; then
	usb_swap_val="Disable"
fi

cat<<-EOF
	<tr><td colspan=9></td>
	<td class="highcol"><input type="submit" name="standby" value="Submit" onClick="return msubmit('power_act')"></td></tr>
	</table>
	</fieldset>
	<fieldset>
	<legend>Swap</legend>
	<table>
	<tr><td>Swapping on USB devices:</td><td><input style="width:100%" type="submit" name=usb_swap value="$usb_swap_val" onClick="return msubmit('usb_swap_act')" $(ttip usb_swap_tt)></td></tr>
	<tr><td>Recreate swap on all devices:</td><td><input style="width:100%" type="submit" name=recreate_swap value=Recreate onClick="return msubmit('recreate_swap_act')" $(ttip recreate_swap_tt)></td></tr>
	<tr><td>Swap aggressiveness:</td><td><input  style="width:100%" type="text" size=4 name=swappiness value=$(cat /proc/sys/vm/swappiness) onChange="return msubmit('swappiness_act')" $(ttip swappiness_tt)></td></tr>
	</table>
	</fieldset>
	</form></body></html>
EOF
