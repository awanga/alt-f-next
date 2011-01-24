#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

check_cookie
write_header "Filesystem Maintenance" "document.diskm.reset()"

cat<<-EOF
	<script type="text/javascript">
	function msubmit(id, part, notflashed) {
		obj = document.getElementById(id)
		opi = obj.selectedIndex
		op = obj.options[opi].value

		res = false
		if (opi == 0)
			return false;

		else if (op == "Format" || op == "Convert") {
			if (document.getElementById("fsfs_" + part).selectedIndex == 0) {
				alert("Select a FS first.")
				obj.selectedIndex = 0
				return false
			}
			if (document.getElementById("fsfs_" + part).selectedIndex == 3 && notflashed == 1) {
				if (! confirm("Your box is not Alt-F flashed and the ext4 filesystem is not recognized by the stock firmware." + '\n' + "Proceed anyway?")) {
					obj.selectedIndex = 0
					return false
				}
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
		else if (op == "setMountOpts")
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
	
cat<<-EOF
	<table><tr align=center><th>Dev.</th><th>Size</th>
	<th>FS</th>
	<th>Label</th>
	<th>Mount Options</th>
	<th>FS Operations</th>
	<th colspan=2>New FS Operations</th>
	</tr>
EOF

# is ntfsprogs pkg installed?
ntfs_dis="disabled"
if test -f /usr/sbin/mkntfs; then
	ntfs_dis=""
fi

isflashed
flashed=$?

blk=$(blkid -c /dev/null -s LABEL -s TYPE) # -s UUID)
ppart=$(cat /proc/partitions)
i=1
for j in $(ls /dev/sd[a-z][1-9] /dev/md[0-9]* 2>/dev/null); do
	part=$(basename $j)

	if test ${part:0:2} = "md"; then
		if ! test -f /sys/block/$part/md/array_state; then continue; fi
		if test "$(cat /sys/block/$part/md/array_state)" = "inactive"; then continue; fi
	else # is an extended partition?
		if test "$(cat /sys/block/${part:0:3}/$part/size)" -le 2; then continue; fi
	fi

	LABEL=""; TYPE="none"
	eval $(echo "$blk" | sed -n '\|^'$j':|s|.*:||p');

	# partitions that where once a component raid can appear as mdraid
	if test "$TYPE" = "swap" -o "$TYPE" = "mdraid"; then continue; fi

	otype=$TYPE

	mount_opts=""
	eval $(awk '{if ($1 == "'$j'") printf "mount_opts=%s", $4}' /etc/fstab)

	all_dis=""
	if test "$TYPE" = "none"; then
		all_dis="disabled"
		otype="<font color=red>$TYPE</font>"
	fi

	conv_en="disabled"
	if test "$TYPE" = "ext2" -o "$TYPE" = "ext3"; then conv_en=""; fi

	clean_en=""; label_en=""
	if test "$TYPE" = "ntfs" -a -n "$ntfs_dis"; then
		clean_en="disabled"
		label_en="disabled"
	fi

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
		mtd="<option>Mount</option>"
	fi

	cat<<-EOF
		<tr>
		<td>$part</td>
		<td align=right>$pcap</td>
	EOF

	fs_progress $part # ln is global
	if test -n "$ln"; then
		cat<<-EOF
			<td><font color=RED>$ln</font></td>
		EOF
	fi

	if test -z "$ln"; then
		cat<<-EOF
			<td align=center>$otype</td>
			<td><input $all_dis type=text size=10 name=lab_$part value="$LABEL"></td>
			<td><input $all_dis type=text size=16 name=mopts_$part value="$mount_opts"></td>
			<td><select id="op_$part" $all_dis name="$part" onChange="msubmit('op_$part', '$part', '$flashed')">
				<option>Operation</option>
				$mtd
				<option $clean_en>Clean</option>
				<option $label_en value=setLabel>Set Label</option>
				<option value=setMountOpts>Set Mnt Options</option>
				<option $resize_en>Shrink</option>
				<option $resize_en>Enlarge</option>
				<option>Wipe</option>
			</select></td>
			<td><select id=fsfs_$part name="type_$part">
				<option>New FS</option>
				<option>ext2</option>
				<option>ext3</option>
				<option>ext4</option>
				<option>vfat</option>
				<option $ntfs_dis>ntfs</option>
			</select></td>
			<td><select id="fs_$part" name="$part" onChange="msubmit('fs_$part', '$part', '$flashed')">
				<option>Operation</option>
				<option >Format</option>
				<option $all_dis $conv_en >Convert</option>
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
	</table></fieldset><br>

	<fieldset><Legend><strong> Set mounted filesystems to be checked every </strong></legend>
	<input type=text size=4 name=TUNE_MOUNTS value=$TUNE_MOUNTS> mounts
	or every <input type=text size=4 name=TUNE_DAYS value=$TUNE_DAYS> days
	<input type=submit name=tune value=Submit>
	</fieldset>
	</form></body></html>
EOF
