#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

check_cookie
write_header "Disk Maintenance" "" "document.diskm.reset()"

cat<<-EOF
	<script type="text/javascript">
	function msubmit(id, part) {
		obj = document.getElementById(id)
		opi = obj.selectedIndex
		op = obj.options[opi].value

		res = false
		if (opi == 0)
			return false;
//  FS ops:
		else if (op == "Format" || op == "Convert") {
			if (document.getElementById("fsfs_" + part).selectedIndex == 0) {
				alert("Select a FS first.")
				obj.selectedIndex = 0
				return false
			}
			if (op == "Format")
				res = confirm("Formating will destroy all data in the partition " + part + "\n\n\
Proceed?");
			else if (op == "Convert")
				res = confirm("Converting filesystems can only be done upwards.\n\n\
It is not advisable to do if you intend to continue using\n\
the vendors firmware, that might not recognize the new format.\n\n\
Proceed converting the " + part + " partition anyway?");
		}
		else if (op == "Mount")
			res = true
		else if (op == "unMount")
			res = true
		else if (op == "Clean")
			res = true
		else if (op == "setLabel")
			res = true
		else if (op == "Shrink")
			res = confirm("Shrink a filesystem only if you intend to latter shrink\n\
the disk partition (or RAID device) where it lays-on,\n\
in order to make more space available in the next partition.\n\
The filesystem will be 5% bigger than the data it contains.\n\nProceed?")
		else if (op == "Enlarge")
			res = confirm("Enlarge a filesystem only if you have made more space\n\
available in the disk partition (or RAID device) where it lays-on.\n\
The filesystem will occupy the whole partition (or RAID device).\n\nProceed?")
		else if (op == "Wipe")
			res = confirm("Wiping a filesystem fills it with zeros, destroing all its data.\n\
The data can only be recovered at specialized data recovery centers.\n\
It runs at about 1GB/min.\n\nProceed?")
// raid ops:

		else if (op == "Remove_bitmap") // write intent bitmap
			res = confirm("Removing the Write Intent Bitmap makes resyncing much slower.\n\n\
Continue?")	
		else if (op == "Create_bitmap") // write intent bitmap
			res = confirm("Creating a Write Intent Bitmap makes resyncing much faster.\n\n\
Continue?")	
		else if (op == "Verify") // raid consistency
			res = true
		else if (op == "Repair") // raid inconsistency
			res = true
		else if (op == "Enlarge_raid") // raid to accomodate bigger partitions
			res = confirm("A RAID device should be enlarged only when all its partition\n\
components are bigger that the RAID size.\n\
The RAID device will have the size of its smaller partition component.\n\
You should afterwards Enlarge the filesystem laying on it.\n\nContinue? ")
		else if (op == "Shrink_raid") // raid to accomodate bigger partitions
			res = confirm("A RAID device should be shrinked only after the filesystem it contains\n\
has already been shrinked.\n\
The RAID device will have the same size as the filesystem it contains.\n\n\
Continue? ")
		else if (op == "Add_part" || op == "Remove_part") {
			if (document.getElementById("rdev_" + part).selectedIndex == 0) {
				alert("Select a Partition first.")
				obj.selectedIndex = 0
				return false
			}
			if (op == "Add_part")
				res = confirm("Add partition to " + part) // partition to raid
			else if (op == "Remove_part")
				res = confirm("Remove partition from " + part) // partition to raid
		}

		if (res == true)
			document.getElementById("diskm").submit();
		else
			obj.selectedIndex=0
	}
	</script>
EOF

has_disks

cat<<-EOF
	<form id="diskm" name="diskm" action="/cgi-bin/diskmaint_proc.cgi" method="post">
	<fieldset><Legend> <strong> Filesystems </strong> </legend>
EOF

#if ! blkid -c /dev/null -s TYPE -o value | 
#	grep -q '\(ext2\|ext3\|ext4\|vfat\|ntfs\)'; then
if false; then
	echo "None"
else
	
	cat<<-EOF
		<table><tr align=center><th>Dev.</th><th>Size</th>
		<th>FS</th>
		<th>Label</th>
		<th>FS Operations</th>
		<th colspan=2>New FS Operations</th>
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
		if test ${part%%[0-9]} = "md"; then
			if test "$(cat /sys/block/$part/md/array_state)" = "inactive"; then
				continue
			fi
		fi
	
		LABEL=""; TYPE="none"
		eval $(echo "$blk" | sed -n '\|^'$j':|s|.*:||p');
	
		# partitions that where once a component raid can appear as mdraid
		if test "$TYPE" = "swap" -o "$TYPE" = "mdraid"; then continue; fi
	
		otype=$TYPE
	
		all_dis=""
		if test "$TYPE" = "none"; then
			all_dis="disabled"
			otype="<font color=red>$TYPE</font>"
		fi
	
		conv_en="disabled"
		if test "$TYPE" = "ext2" -o "$TYPE" = "ext3"; then conv_en=""; fi
	
		clean_en=""
		if test "$TYPE" = "ntfs" -a -z "$mk_ntfs"; then clean_en="disabled"; fi
	
		resize_en=""
		if test "$TYPE" = "vfat" -o "$TYPE" = "ntfs"; then
			resize_en="disabled"
			otype="<font color=blue>$TYPE</font>"
		fi
	
		if isdirty $part; then otype="<font color=red>$TYPE</font>"; fi

		if ismount $part; then
			# only works for mounted partitions
			pcap=$(df -h /dev/$part | awk '/'$part'/{printf "%sB", $2}')
			mtd="<option value=unMount>Unmount</option>"
		else
			# filesystem does not have to fill the partiton, signal it
			pcap=$(awk '/'$part'/{printf "<font color=blue>%.1fGB</font>", $3/1048576}' /proc/partitions)
			mtd="<option>Mount</option"
		fi
	
		cat<<-EOF
			<tr>
			<td>$part</td>
			<td align=right>$pcap</td>
		EOF
	
		working=""
		for k in clean format convert shrink enlarg wip; do
			if test -f /tmp/$k-$part; then
				#if test -d /proc/$(cat /tmp/$k-$part.pid); then
				if kill -1 $(cat /tmp/$k-$part.pid) 2> /dev/null; then
					working="yes"
					echo "<td><font color=RED>${k}ing</font></td></tr>"
				else
					rm -f /tmp/$k-$part*
				fi
			fi
		done
	
		if test -z "$working"; then
			cat<<-EOF
				<td align=center>$otype</td>
				<td><input $all_dis type=text size=10 name=lab_$part value="$LABEL"></td>
				<td><select id="op_$part" $all_dis name="$part" onChange="msubmit('op_$part', '$part')">
					<option>Operation</option>
					$mtd
					<option $clean_en>Clean</option>
					<option value=setLabel>Set Label</option>
					<option $resize_en>Shrink</option>
					<option $resize_en>Enlarge</option>
					<option>Wipe</option>
				</select</td>
				<td><select id=fsfs_$part name="type_$part">
					<option>New FS</option>
					<option>ext2</option>
					<option>ext3</option>
					<option>ext4</option>
					<option>vfat</option>
					<option $ntfs_dis>ntfs</option>
				</select></td>
				<td><select id="fs_$part" name="$part" onChange="msubmit('fs_$part', '$part')">
					<option>Operation</option>
					<option >Format</option>
					<option $all_dis $conv_en >Convert</option>
				</select></td></tr>
			EOF
		fi
		i=$((i+1))
	done

fi # no filesystems

CONFT=/etc/misc.conf

if test -f $CONFT; then
	. $CONFT
fi
if test -z "$TUNE_MOUNTS"; then
	TUNE_MOUNTS=50
fi
if test -z "$TUNE_DAYS"; then
	TUNE_DAYS=180
fi

cat<<-EOF
	</table></fieldset><br>

	<fieldset><Legend><strong> Set mounted filesystems to be checked every </strong></legend>
	<input type=text size=4 name=TUNE_MOUNTS value=$TUNE_MOUNTS> mounts
	or every <input type=text size=4 name=TUNE_DAYS value=$TUNE_DAYS> days
	<input type=submit name=tune value=Submit>
	</fieldset><br>

	<fieldset><Legend> <strong> RAID </strong> </legend><table>
EOF

if ! blkid -c /dev/null -t TYPE=mdraid >& /dev/null; then
	echo "None<br>"
else
	cat<<-EOF
		<tr align=center>
		<th align=left>Dev.</th> 
		<th>Capacity</th>
		<th>Level</th>
		<th>Components</th>
		<th>Array</th>
		<th>RAID Operations</th>
		<th colspan=2>Partition Operations</th>
 		</tr>
	EOF

	raid_devs="<option value=none>Partition</option>"
#	raidp="$(blkid -c /dev/null | awk '/mdraid/{print substr($1, 6, 4)}')"
	raidp="$(fdisk -l | awk '$5 == "da" || $5 == "fd" { print substr($1, 6)}')"

	for j in $raidp; do
		cap="$(awk '{printf "%.0f", $0*512/1e9}' /sys/block/${j:0:3}/$j/size)"
		raid_devs="$raid_devs<option value=$j>$j ${cap}GB</option>"
	done

#	alldevs=""	
	if ls /dev/md? >& /dev/null; then
		for i in /dev/md[0-9]*; do
			mdev=$(basename $i)
	
			state=$(cat /sys/block/$mdev/md/array_state)
			type=$(cat /sys/block/$mdev/md/level)
			pcap=$(awk '/'$mdev'/{printf "%.1f GB", $3/1048576}' /proc/partitions)
	
			devs=""
			for i in $(ls /sys/block/$mdev/slaves); do
				if test $(cat /sys/block/$mdev/md/dev-$i/state) = "faulty"; then
					devs="$devs <font color=RED>$i</font>"
				elif test $(cat /sys/block/$mdev/md/dev-$i/state) = "spare"; then
					devs="$devs <font color=GREEN>$i</font>"
				else
					devs="$devs $i"
				fi
#				alldevs="$alldevs $i"
			done
	
			otype=$type
			if test "$(cat /sys/block/$mdev/md/degraded 2>/dev/null )" = 1; then
				otype="<font color=RED>$type</font>"
			fi
	
			cat<<-EOF
				<tr align=center>
				<td align=left>$mdev</td> 
				<td>$pcap</td>
				<td>$otype</td>
				<td>$devs</td>
			EOF
	
			if ! test "$type" = "raid1" -o "$type" = "raid5"; then
				echo "<td><input type=submit name=$mdev value=\"Stop\"</td></tr>"
				continue
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
					<td><font color=RED> ${action}ing </font>
					<input type=submit name=$mdev value="Abort"></td>
					</tr>
				EOF
			else
				cat<<-EOF
					<td><input type=submit name=$mdev value="Stop"</td>		
					<td><select id="raidop_$mdev" name="$mdev" onChange="msubmit('raidop_$mdev', '$mdev')">
						<option>Operation</option>
						<option value=${bitmap}_bitmap>$bitmap Bitmap</option>
						<option>Verify</option>
						<option>Repair</option>
						<option value="Enlarge_raid">Enlarge</option>
						<option value="Shrink_raid">Shrink</option>
					</select</td>
					<td><select id=rdev_$mdev name=rdev_$mdev>$raid_devs</select></td>
					<td><select id=rops_$mdev name=$mdev onChange="msubmit('rops_$mdev', '$mdev')">
						<option value=none>Operation</option>
						<option value=Add_part>Add</option>
						<option value=Remove_part>Remove</option>"
					</select></td>
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
			/Preferred Minor/ { printf "rdev=\"md%d\"; ", $4}
			/this/ { getline; while (getline) {
				if (substr($NF, 1,5) == "/dev/") {
					devs = substr($NF, 6, 4) " " devs;}}
				printf "devs=\"%s\";", devs}')
		if test -b /dev/$rdev; then continue; fi
		if echo "$ex" | grep -q "$rdev" ; then continue; fi
		ex="$rdev $ex"
#if echo "$alldevs" | grep -q $i; then continue; fi
#alldevs="$alldevs $devs"
#echo "<p>$alldevs</p>"

		cat<<-EOF
			<tr align=center>
			<td>$rdev</td>
			<td></td>
			<td>$level</td>
			<td>$devs</td>
			<td><input type=submit name=$rdev value="Start"</td>
			</tr>
		EOF
	done
fi

cat<<-EOF
	</table></fieldset><br>
	</form></body></html>
EOF
