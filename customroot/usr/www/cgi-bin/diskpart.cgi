#!/bin/sh

. common.sh
check_cookie
write_header "Disk Partitioner" "" "document.diskp.reset()"

has_disks

mktt keep_id "If checked, no changes will be made to this partition."

cat<<-EOF
	<script type="text/javascript">
	function opsubmit(disk, bay, cap) {
		obj = document.getElementById("op_" + disk)
		idx = obj.selectedIndex
		op = obj.options[idx].value

		ret = false
		if (op == "Operation") {
			alert("Select an operation to perform on the disk.")
		}
		else if (op == "Erase") {
			ret = confirm('The ' + cap + ' GB ' + bay + ' disk partition table will be erased,\n\
and all disk data will become inacessible.\n\nContinue?')
		}
		else if (op == "Save") {
			alert('The ' + cap + ' GB ' + bay + ' disk partition table will be saved as /tmp/saved_' + disk + '_part.\n\
It will disappear after a reboot or powerdown.')
			ret = true
		}
		else if (op == "Load") {
			ret = confirm('You are going to write the ' + cap + ' GB ' + bay + ' disk\n\
 partition table  with a previously saved one.\n\nContinue?') 
		}

		if (ret == false) {
			obj.selectedIndex = 0
			return false
		}

		obj.value = op
		document.diskp.submit()
		return ret
	}

	function msubmit(frompart, frombay, fromsz) {
		obj = document.getElementById("cp_" + frompart)
		idx = obj.selectedIndex
		topart = obj.options[idx].value

		ret = false
		if (topart == frompart) {
			alert("Select a destination disk different from the origin disk.")
			obj.selectedIndex = 0
		}
		else if (topart == "CopyTo") {
			alert("Select a destination disk.")
			obj.selectedIndex = 0
		} else {
			ret = confirm("The partition table of the " + frompart + " disk will be copied" + '\n' + "to the " + topart + " disk, " + \
"making all " +  topart + " disk data inacessible." + '\n' + '\n' + "Continue?")
		}

		if (ret == false) {
			obj.selectedIndex = 0
			return false
		}
		document.diskp.cp_from.value = frompart
		document.diskp.submit()
	}

	function keeppart(ipart) {
		st = document.getElementById("keep_" + ipart).checked;
		document.getElementById("cap_" + ipart).disabled = st;
		document.getElementById("type_" + ipart).disabled = st;
	}

	function updatefree(dcap, dsk, part) {
		free = dcap;
		for (i=1; i<=4; i++)
			free -= document.getElementById("cap_" + dsk + i).value*1000;
		document.getElementById("free_id").value = free/1000;

		if (document.getElementById("cap_" + part).value == 0)
			document.getElementById("type_" + part).selectedIndex = 0;
	}

	function psubmit(diskcap, bay, free) {
		if (document.getElementById("free_id").value < 0 ) {
			alert("The sum of the partitions size is greater than the disk capacity.\n\
Decrease the size of some partitions and retry.")
			return false
		}
		
		return confirm("Partitioning the " + diskcap + " GB " + bay + " disk can make all its data inacessible.\n\nContinue?")
	}

	function reopen(dsk) {
		url=window.location + "?disk=" + dsk;
		window.location.assign(url)
	}

	</script>
	<form id=diskp name=diskp action="/cgi-bin/diskpart_proc.cgi" method="post">
EOF

if test -n "$QUERY_STRING"; then
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')
	dsk="/dev/$(httpd -d "$disk")"
else
	eval $(cat /etc/bay | sed -n 's/ /=/p')
	for i in $right $left $usb; do
		if test -n "$i"; then
			dsk="/dev/$i"
			break
		fi
	done
fi

ntfsopt="disabled"
if test -f /usr/sbin/mkntfs; then
	ntfsopt=""
fi

cat<<-EOF
	<fieldset>
	<legend><strong>Select the disk you want to partition</strong></legend>
	<table><tr>
	<th>Partition</th>
	<th>Bay</th>
	<th>Device</th>
	<th>Capacity</th>
	<th>Model</th>
	<th colspan=2>Partition Table</th>
	</tr>
EOF

opt_disks="$(for i in $disks; do echo "<option>$(basename $i)</option>"; done)"
opt_disks="<option>CopyTo</option> $opt_disks"
 
for i in $disks; do
	disk=$(basename $i)

	mod=$(disk_name $disk)
	cap=$(awk '{printf "%.1f", $1*512/1e9}' /sys/block/$disk/size)
	bay=$(awk '/'$disk'/{print toupper($1)}' /etc/bay)

	chkd=""	
	if test "$i" = "$dsk"; then chkd="checked"; fi

	cat<<-EOF
		<tr>
		<td><input type=radio $chkd name=disk value=$disk onchange="reopen('$disk')"></td>
		<td>$bay</td>
		<td align=center>$disk</td>
		<td align=right>$cap GB</td>
		<td>$mod</td>
		<td><select id=op_$disk name=op_$disk onChange="opsubmit('$disk','$bay','$cap')">
			<option>Operation</option>
			<option>Erase</option>
			<option>Save</option>
			<option>Load</option>
		</select></td>
		<td><select id=cp_$disk name=cp_$disk onChange="msubmit('$disk','$bay', '$cap')">$opt_disks</select></td>
		</tr>
	EOF
done

echo "<input type=hidden name=cp_from>"
echo "</table></fieldset><br>"	

ddsk=$(basename $dsk)
rawcap=$(expr $(sfdisk -s $dsk) \* 1024 / 1000000)

mod=$(disk_name $ddsk)
diskcap=$(awk '{printf "%.1f", $1*512/1e9}' /sys/block/$ddsk/size)
bay=$(awk '/'$ddsk'/{print toupper($1)}' /etc/bay)

cat<<-EOF
	<fieldset>
	<legend><strong>Partition $bay disk, $diskcap GB, $mod </strong></legend>
	<table>
	<tr align=center>
	<th> Keep </th>
	<th> Part. </th>
	<th> Type </th>
	<th> Size (GB) </th>
	<th> Type </th>
	</tr>
EOF

fout=$(sfdisk -l $dsk | tr '*' ' ') # *: the boot flag...

keepchk="checked"
keepdis="disabled"
if $(echo $fout | grep -q "No partitions found"); then
	fout="${dsk}1          0       -       0          0    0  Empty
${dsk}2          0       -       0          0    0  Empty
${dsk}3          0       -       0          0    0  Empty
${dsk}4          0       -       0          0    0  Empty"
keepchk=""
keepdis=""
fi

used=0
for pl in 1 2 3 4; do
	part=${dsk}$pl
	ppart=$(basename $part)
	id=""; type="";cap=""
	eval $(echo "$fout" | awk '
		/'$ppart'/{printf "id=\"%s\" type=\"%s\"; cap=%.1f; rcap=%d", \
		$6, substr($0, index($0,$7)), $5*1024/1e9, $5}')

	used=$((used + rcap))

	emptys=""; swaps=""; linuxs=""; raids=""; vfats=""; ntfss=""; extendeds=""
	case $id in
		0) emptys="selected" ;;
		82) swaps="selected" ;;
		83) linuxs="selected" ;;
		5|f|85) extendeds="selected" ;;
		fd|da) raids="selected"	;;
		b|c) vfats="selected" ;;
		7) ntfss="selected" ;;
	esac

	cat<<-EOF
	<tr>
	<td align=center><input type="checkbox" $extendeddis $keepchk id="keep_$ppart" name="keep_$ppart" value="yes" 
		onclick="keeppart('$ppart')" $(ttip keep_id)></td>
	<td>$ppart</td>
	<td>$type</td>
	<td><input type=text $keepdis size=6 id=cap_$ppart name=cap_$ppart 
		value=$cap onchange="updatefree('$rawcap', '$ddsk', '$ppart')"></td>
	<td><select $keepdis id=type_$ppart name=type_$ppart>
	<option $emptys>empty</option>
	<option $raids>RAID</option>
	<option $swaps>swap</option>
	<option $linuxs>linux</option>
	<option $vfats>vfat</option>
	<option $ntfss $ntfsopt>ntfs</option>
	<option $extendeds disabled>extended</option>
	</select></td>
	</tr>
	EOF

done 

free="$(expr $rawcap - $used \* 1024 / 1000000)"
free=$(awk 'BEGIN {printf "%.3f", ('$rawcap' - '$used' * 1024/1e6)/1000}')

cat<<-EOF
	<tr><td colspan=2></td>
	<td align=right>Free</td>
	<td><input type=text readonly id="free_id" size=6 value="$free"></td>
	</tr>
	<tr><td align=center colspan=2><input type=submit name=$ddsk value=Partition
		onclick="return psubmit('$diskcap', '$bay', '$free')"></td>
	</tr>
	</table></fieldset><br>
	</form></body></html>
EOF
