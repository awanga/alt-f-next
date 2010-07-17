#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

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

. common.sh

check_cookie
write_header "Disk Maintenance"

s="<strong>"
es="</strong>"
c="<center>"
ec="</center>"

cat<<-EOF
	<script type="text/javascript">
	function ask(msg) {
		return confirm(msg); 
	}
	</script>
EOF

disks=$(ls /dev/sd?) >/dev/null 2>&1

if test -z "$disks"; then
        echo "<br> $s No disks found! $es <br>"
        echo "</body></html>"
        exit 1
fi

CONFF=/etc/hdsleep.conf
CONFT=/etc/tune.conf

. /tmp/power_mode

if test -f $CONFF; then
	while read  line; do
		eval $(echo $line | awk '!/#/{if (NF == 2) print $1 "=" $2}')
	done < $CONFF
else
	right=90
	left=90
	usb=90	
	echo -e "right $right\nleft $left\nusb $usb"
fi

if test -f $CONFT; then
	while read  line; do
		eval $(echo $line | awk '!/#/{if (NF == 2) print $1 "=" $2}')
	done < $CONFT
else
	mounts=50
	days=180
	echo -e "mounts $mounts\ndays $days"
fi

cat<<EOF
	<form action="/cgi-bin/diskutil_proc.cgi" method="post">
	<fieldset><Legend> $s Disks $es </legend>
	<table>
	<tr align=center><th>Bay</th>
	<th>Dev.</th>
	<th>Disk Model</th>
	<th></th>
	<th>Health</th>
	<th>P. Mode</th>
	<th></th>
	<th columnspan=2>Set Standby</th> 
EOF

while read ln; do
	if test -z "$ln"; then continue; fi
	eval $(echo $ln | awk '{printf "bay=%s;dsk=%s", $1, $2}')
	stat=$(dstatus $dsk)
	poweren=""
	if test "$stat" = "unknown"; then poweren="disabled"; fi
	mod=$(cat /sys/block/$dsk/device/model)
	eval "val=\$$bay"
 
	echo "<tr><td> $s $bay $es </td><td>$dsk</td><td> $mod </td>"

	if ! test -b "/dev/$dsk"; then
		echo "<td></td><td></td><td></td><td></td>"
	else
		cat<<-EOF	 
			<td> <input type="submit" name="$dsk" value="Eject"> </td>
			<td> <input type="submit" name="$dsk" value="Status"> </td>
			<td> $stat </td>
			<td> <input type="submit" $poweren name="$dsk" value="StandbyNow"> </td>
		EOF
	fi

	echo "<td><input type="text" size=4 name="$bay" value="$val"> minutes</td></tr>"
done < /etc/bay

cat<<-EOF
	<tr>
	<td colspan=7></td>
	<td><input type="submit" name="standby" value="Submit"> </td>
	</tr>        
	</table>
	</fieldset><br>

	<fieldset><Legend> $s Filesystems $es </legend>
	<table><tr align=center><th>Dev.</th><th>Size</th><th>FS</th>
	<!--th>Dirty</th-->
	<th>Label</th>
	<th></th><th></th><th></th><th>New FS</th>
	<th colspan=2>To New FS</th>
	</tr>
EOF

# is ntfsprogs pkg installed?
ntfs_dis="disabled"
if test -f /usr/sbin/mkntfs; then
	ntfs_dis=""
fi

blk=$(blkid -c /dev/null -s LABEL -s TYPE)
i=1
for j in $(ls /dev/sd[a-z][1-9] /dev/md[0-9]* 2>/dev/null); do
	part=$(basename $j)
	##TYPE=$(blkid -s TYPE -o value $j)
	##LABEL=$(blkid -s LABEL -o value $j | tr ' ' '_')
	LABEL=""; all_dis=""; TYPE="<font color=red>none</font>"
	eval $(echo "$blk" | sed -n '\|^'$j':|s|.*:||p');

	if test "$TYPE" = "<font color=red>none</font>"; then all_dis="disabled"; fi

	if test "$TYPE" = "swap" -o "$TYPE" = "mdraid"; then continue; fi

	conv_en="disabled"
	if test "$TYPE" = "ext2" -o "$TYPE" = "ext3"; then conv_en=""; fi

	clean_en=""
	if test "$TYPE" = "ntfs" -a -z "$mk_ntfs"; then clean_en="disabled"; fi

	#if test -z "$LABEL"; then LABEL=$part; fi
	if grep -q ^$j /proc/mounts; then mtd="unMount"; else mtd="Mount"; fi

	pcap=$(awk '/'$part'/{printf "%.1f", $3/1048576}' /proc/partitions)

	cat<<-EOF
		<tr>
		<td>$part</td>
		<td align=right>$pcap GB</td>
	EOF

	working=""
	for k in clean format convert; do
		if test -f /tmp/$k-$part; then
			if test -d /proc/$(cat /tmp/$k-$part.pid); then
				working="yes"
				echo "<td></td><td></td><td><font color=RED>${k}ing</font></td></tr>"
			else
				rm -f /tmp/$k-$part*
			fi
		fi
	done

	if test -z "$working"; then
	
		dirty="";
		if isdirty $part; then dirty="<font color=red>*</font>"; fi
		if test "$TYPE" = "<font color=red>none</font>"; then dirty=""; fi

		cat<<-EOF
			<td>$TYPE</td>
			<!--td align=center>$dirty</td-->
			<td><input $all_dis type=text size=10 name=lab_$part value="$LABEL"></td>
			<td><input $all_dis type=submit name=$part value="setLabel"></td>
			<td><input $all_dis type=submit name=$part value="$mtd"></td>
			<td><input $all_dis type=submit $clean_en name=$part value="Clean"></td>
			<td><select name=type_$part>
			<option value=ext2>ext2</option>
			<option value=ext3>ext3</option>
			<option selected value=ext4>ext4</option>
			<option value=vfat>vfat</option>
			<option $ntfs_dis value=ntfs>ntfs</option>
			</select></td>
			<td><input $all_dis type=submit $conv_en name=$part value="Convert"
				onclick="return ask('Converting a filesystem can only be done upwards.\n\nIt is not advisable to do if you intend to continue using\n the vendors firmware, that might not recognize the new format.\n\nProceed anyway?')"></td>
			<td><input type=submit name=$part value="Format" 
				onclick="return ask('Formating will destroy all data in the partition \'$part\' labeled \'$LABEL\'.\n\nProceed?')"></td>
			</tr>
		EOF
	fi
	i=$((i+1))
done

cat<<-EOF
	</table></fieldset><br>
	<fieldset><Legend> $s Set mounted partitions to be checked every $es </legend>
	<input type=text size=4 name=mounts value=$mounts> mounts
	or every <input type=text size=4 name=days value=$days> days
	<input type=submit name=tune value=Submit>
	</fieldset><br>
	<fieldset><Legend> $s RAID $es </legend><table>
EOF

if ! blkid -c /dev/null -t TYPE=mdraid >& /dev/null; then
	echo "None<br>"
#if ! test -e /proc/mdstat; then
#	echo "None<br>"
#elif test -z "$(grep ^md /proc/mdstat)"; then
#	echo "None<br>"
else
	cat<<-EOF
		<tr align=center>
		<th align=left>Dev.</th> 
		<th>Capacity</th>
		<th>Level</th>
		<!--th>State</th-->
		<th>Components</th>
		<th>Array</th>
		<!--th>Deg.</th-->
		<th>Grow</th>
		<th>Intent<br>Bitmap</th>
		<th colspan=2>Consistency</th>
		<th colspan=3>Component Operations</th> 
 		</tr>
	EOF

	raid_devs="<option value=none>Partition</option>"
#	raidp="$(blkid -c /dev/null | awk '/mdraid/{print substr($1, 6, 4)}')"
	raidp="$(fdisk -l | awk '$5 == "da" || $5 == "fd" { print substr($1, 6)}')"

	for j in $raidp; do
		cap="$(awk '{printf "%.0f", $0*512/1e9}' /sys/block/${j:0:3}/$j/size)"
		raid_devs="$raid_devs<option value=$j>$j ${cap}GB</option>"
	done

	raid_ops="<option value=none>Operation</option>
		<option value=add>Add</option>
		<option value=remove>Remove</option>"

if ls /dev/md? >& /dev/null; then
	for i in /dev/md[0-9]*; do
		mdev=$(basename $i)

		state=$(cat /sys/block/$mdev/md/array_state)
		type=$(cat /sys/block/$mdev/md/level)
		pcap=$(awk '/'$mdev'/{printf "%.1f", $3/1048576}' /proc/partitions)

		devs="$(cat /proc/mdstat | awk '
			/'$mdev'/ {printf ("%.4s %.4s %.4s", $5, $6, $7)}')"

		cat<<-EOF
			<tr align=center>
			<td align=left>$mdev</td> 
			<td>$pcap GB</td>
			<td>$type</td>
			<!--td>$state</td-->
			<td>$devs</td>
		EOF

		if ! test "$type" = "raid1" -o "$type" = "raid5"; then
			echo "<td><input type=submit name=$mdev value=\"Stop\"</td></tr>"
			continue
		fi

		deg=""
		if test "$(cat /sys/block/$mdev/md/degraded)" != 0; then
			deg="<font color=RED>*</font>"
		fi

		bitmap="Remove"
		if test "$(cat /sys/block/$mdev/md/bitmap/location)" = "none"; then
			bitmap="Create"
		fi

		action="idle"
		if test -f /sys/block/$mdev/md/sync_action; then
			action=$(cat /sys/block/$mdev/md/sync_action)
		fi

		if test "$action" != "idle"; then
			cat<<-EOF
				<td><font color=RED> ${action}ing </font></td>
				<!--td><input type=submit name=$mdev value="Abort"></td-->
				</tr>
			EOF
		else

#		grow="Grow"
#		after changing onecomponent to a bigger one, grow the
#		array. The write-intent bitmap must be removed first.
			cat<<-EOF
				<td><input type=submit name=$mdev value="Stop"</td>
				<!--td>$deg</td-->
				<td><input type=submit name=$mdev value="Grow"></td>
				<td><input type=submit $bit_en name=$mdev value="$bitmap"></td>
				<td><input type=submit name=$mdev value="Check"></td>
				<td><input type=submit name=$mdev value="Repair"></td>
				<td><select name=rdev>$raid_devs</select></td>
				<td><select name=rops>$raid_ops</select></td>
				<td><input type=submit name=$mdev value="Apply"></td>
				</tr>
			EOF
		fi
	done
fi

# "Preferred Minor" is for 0.9 metadata
# minor can be extracted from "name" with 1.x metadata
# create with 0.9 metadata? for compatibility with the vendor's firmware?

	ex=""
	for i in $raidp; do
		eval $(mdadm --examine /dev/$i 2> /dev/null | awk '
			/Raid Level/ { printf "level=%s; ", $4}
			/Preferred Minor/ { printf "rdev=md%d; ", $4}
			/this/ { getline; while (getline) {
				devs = substr($8, 6, 4) " " devs;}
				printf "devs=\"%s\";", devs}')
		if test -b /dev/$rdev; then continue; fi
		if echo "$ex" | grep -q $rdev ; then continue; fi
		ex="$rdev $ex"
		cat<<-EOF
			<tr align=center>
			<td>$rdev</td>
			<td></td>
			<td>$level</td>
			<td></td>
			<td>$devs</td>
			<td><input type=submit name=$rdev value="Start"</td>
			</tr>
		EOF
	done

fi

cat<<EOF
	</table></fieldset><br>
	</form></body></html>
EOF
