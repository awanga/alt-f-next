#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

check_cookie
write_header "Filesystem Maintenance" "document.diskm.reset()"

cat<<-EOF
	<script type="text/javascript">
	function msubmit(id, part) {
		obj = document.getElementById(id)
		opi = obj.selectedIndex
		op = obj.options[opi].value

		cmsg = "During the process the filesystem will be unavailable for usage\n\
but the operation evolution can be verified in the status page.\n\n"

		res = false
		if (opi == 0)
			return false;

		else if (op == "Format" || op == "Convert") {
			if (document.getElementById(id).selectedIndex == 0) {
				alert("Select a FS first.")
				obj.selectedIndex = 0
				return false
			}

			if (op == "Format")
				res = confirm("Formatting will destroy all data in the filesystem " + part + "\n\n" + cmsg + "Proceed?");
			else if (op == "Convert")
				res = confirm("Converting filesystems can only be done upwards.\n\n\
It is not advisable to do if you intend to continue using\n\
the vendors firmware, that might not recognize the new format.\n\n" + cmsg +
"Proceed converting the " + part + " filesystem anyway?");
		}
		else if (op == "Mount" || op == "unMount" || op == "setLabel" || op == "setMountOpts" || op == "Details")
			res = true
		else if (op == "Check")
			res = confirm("Cleaning a filesystems means verifying its consistency\n\
and automatically repairing it if necessary and possible.\n\n\
If a major problem is found, the filesystem will not be repaired\n\
and will be mounted read-only.\n\
If this happens, you must either select the \"Force Fix\" Operation\n\
or fix the filesystem using the command line.\n\n" + cmsg + "Proceed checking the " + part + " filesystem?");
		else if (op == "ForceFix")
			res = confirm("Use ONLY if the Check operation failed and asked for manual intervention, as data loss might occur.\n\n" + cmsg + "Are you really sure that you want to force fix the " + part + " filesystem?");
		else if (op == "Shrink")
			res = confirm("Shrinking a filesystem compacts all its data at the partition begin.\n\n\
Shrink a filesystem if you intend to latter shrink the disk partition\n\
(or RAID device) where it lays-on, in order to make more space\n\
available for the next partition.\n\
At the end the filesystem will be only 5% bigger than the data it contains.\n\n" + cmsg + "Proceed?")
		else if (op == "Enlarge")
			res = confirm("Enlarging a filesystem makes it possible to use all available\n\
space in the partition where it lays-on.\n\n\
Enlarge a filesystem only if you have made more space\n\
available in the disk partition (or RAID device) where it lays-on.\n\
At the end the filesystem can use the whole partition (or RAID device).\n\n" + cmsg + "Proceed?")
		else if (op == "Wipe")
			res = confirm("Wiping a filesystem fills it with zeros, destroing all its data.\n\
The data can only be recovered at specialized data recovery centers.\n\
It runs at about 1GB/min.\n\n" + cmsg + "Proceed?")

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
	<fieldset><legend>Filesystems</legend>
EOF
	
cat<<-EOF
	<table>
	<tr><th>Dev.</th><th>Size</th>
	<th>FS</th>
	<th>Mnt</th>
	<th>Label</th>
	<th>Mount Options</th>
	<th>FS Operations</th>
	<th class="highcol" colspan=2>New FS Operations</th>
	</tr>
EOF

# is ntfsprogs pkg installed?
ntfs_dis="disabled"
if test -x /usr/sbin/mkntfs; then
	ntfs_dis=""
fi

# is btrfs-progs installed?
btrfs_dis="disabled"
if test -x /usr/bin/btrfs; then
	btrfs_dis=""
fi

blk=$(blkid -s LABEL -s TYPE)

ppart=$(cat /proc/partitions)
i=1
for j in $(ls /dev/sd[a-z]* /dev/md[0-9]* /dev/dm-[0-9]* 2> /dev/null); do
	part=$(basename $j)
	dname=$part

	if test ${part:0:2} = "md"; then # RAID
		if ! test -f /sys/block/$part/md/array_state; then continue; fi
		if test "$(cat /sys/block/$part/md/array_state)" = "inactive"; then continue; fi
	elif test ${part:0:3} = "dm-"; then # device mapper, LVM or dm-crypt
		# show LV name?
		dname=$(cat /sys/block/$part/dm/name)
		# don't show internal LVM devices for mirror, snapshot, etc volumes
		if echo $dname | grep -qE '_mlog|_mimage|-real|-cow|-pvmove|-missing_'; then continue; fi
	# non-partitioned disk, filesystem uses all device
	elif blkid /dev/$part >& /dev/null; then
		if ls /sys/block/$part/${part}? >& /dev/null; then continue; fi
	# standard partitioned disk
	elif ! test -d /sys/block/${part:0:3}/$part; then
		continue
	# is an extended partition?
	elif test "$(cat /sys/block/${part:0:3}/$part/size)" -le 2; then
		continue
	fi

	LABEL=""; TYPE="none"
	eval $(echo "$blk" | sed -n '\|^'$j':|s|.*:||p');

	if test "$TYPE" = "swap" -o "$TYPE" = "mdraid" \
		-o "$TYPE" = "lvm2pv" -o "$TYPE" = "crypt_LUKS"; then
		continue
	fi

	if find /sys/block/md*/slaves/$part >& /dev/null ; then continue; fi

	otype=$TYPE

	mount_opts=""
	eval $(awk '{if ($1 == "'$j'") printf "mount_opts=%s", $4}' /etc/fstab)

	all_dis=""
	if test "$TYPE" = "none"; then
		all_dis="disabled"
		otype="<span class=\"red\">$TYPE</span>"
	fi

	conv_en="disabled" # FIXME: btrfs convert seems broken!
	if test "$TYPE" = "ext2" -o "$TYPE" = "ext3"; then conv_en=""; fi

	details_en="disabled" # FIXME: implement btrfs details
	if test "$TYPE" = "ext2" -o "$TYPE" = "ext3" -o "$TYPE" = "ext4"; then details_en=""; fi

	clean_en=""; label_en=""
	if test "$TYPE" = "ntfs" -a -n "$ntfs_dis"; then
		clean_en="disabled"
		label_en="disabled"
# 	elif test "$TYPE" = "btrfs"; then
# 		clean_en="disabled"
# 		if test -n "$btrfs_dis"; then
# 			label_en="disabled"
# 		fi
	fi

	resize_en=""
	if test "$TYPE" = "vfat" -o "$TYPE" = "ntfs"; then
		resize_en="disabled"
		otype="<span class=\"blue\">$TYPE</span>"
	fi

	if isdirty $part; then otype="<span class=\"red\">$TYPE</span>"; fi

	mtdf=""
	if ismount $part; then
		# only works for mounted partitions
		pcap=$(df -h /dev/$part | awk '/'$part'/{printf "%sB", $2}')
		mtd="<option value=unMount>Unmount</option>"
		mtdf="*"
	else
		# filesystem does not have to fill the partiton, signal it
		pcap=$(awk '/'$part'$/{printf "<span class=\"blue\">%.1fGB</span>", $3/1048576}' /proc/partitions)
		mtd="<option>Mount</option>"
	fi

	cat<<-EOF
		<tr>
		<td><input type=hidden name=part_$i value="$part">$dname</td>
		<td align=right>$pcap</td>
	EOF

	fs_progress $part # ln is global
	if test -n "$ln"; then
		echo "<td class=\"red\">$ln</td>"
	fi

	if test -z "$ln"; then
		cat<<-EOF
			<td align=center>$otype</td>
			<td align=center>$mtdf</td>
			<td><input $all_dis type=text size=10 name=lab_$i value="$LABEL"></td>
			<td><input $all_dis type=text size=16 name=mopts_$i value="$mount_opts"></td>
			<td><select id="op_$i" $all_dis name="$i" onChange="msubmit('op_$i', '$part')">
				<option>Operation</option>
				$mtd
				<option $clean_en>Check</option>
				<option $clean_en>ForceFix</option>
				<option $label_en value=setLabel>Set Label</option>
				<option value=setMountOpts>Set Mnt Options</option>
				<option $resize_en>Shrink</option>
				<option $resize_en>Enlarge</option>
				<option $details_en>Details</option>
				<option>Wipe</option>
			</select></td>
			<td class="highcol"><select id="fs_$i" name="type_$i">
				<option>New FS</option>
				<option>ext2</option>
				<option>ext3</option>
				<option>ext4</option>
				<option $btrfs_dis>btrfs</option>
				<option>vfat</option>
				<option $ntfs_dis>ntfs</option>
			</select></td>
			<td class="highcol"><select id="fsfs_$i" name="$i" onChange="msubmit('fsfs_$i', '$part')">
				<option>Operation</option>
				<option>Format</option>
				<option $all_dis $conv_en>Convert</option>
			</select></td></tr>
		EOF
	fi
	i=$((i+1))
done

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
	</table></fieldset>

	<fieldset><legend>Set mounted filesystems to be checked every</legend>
	<input type=text size=4 name=TUNE_MOUNTS value="$TUNE_MOUNTS"> mounts
	or every <input type=text size=4 name=TUNE_DAYS value="$TUNE_DAYS"> days
	<input type=submit name=tune value=Submit>
	</fieldset>
	</form></body></html>
EOF
