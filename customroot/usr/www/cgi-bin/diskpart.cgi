#!/bin/sh

. common.sh
check_cookie
write_header "Disk Partitioner" "" "document.diskp.reset()"

has_disks

mktt tt_keep "If checked, no changes will be made to this partition."
mktt tt_psize "Partition size. Rounding can occur."
mktt tt_pstart "Partition start sector."
mktt tt_plen "Partition lenght, in sectors."
mktt tt_free "Free disk space. Rounding can occur."

cat<<-EOF
	<script type="text/javascript">
	// Erase, Save and Load operations
	function opsubmit(disk, bay, cap) {
		obj = document.getElementById("op_" + disk)
		idx = obj.selectedIndex
		op = obj.options[idx].value

		ret = false
		if (op == "Operation") {
			alert("Select an operation to perform on the disk.")
		}
		else if (op == "Erase") {
			ret = confirm('The ' + cap + ' ' + bay + ' disk partition table will be erased,\n\
and all disk data will become inacessible.\n\nContinue?')
		}
		else if (op == "Save") {
			alert('The ' + cap + ' ' + bay + ' disk partition table will be saved as /tmp/saved_' + disk + '_part.\n\
It will disappear after a reboot or powerdown.')
			ret = true
		}
		else if (op == "Load") {
			ret = confirm('You are going to write the ' + cap + ' ' + bay + ' disk\n\
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

	// Copy partition operation
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

	function advanced(dcap, disk) {
		st = document.getElementById("adv_id").value == "Advanced" ? true : false 
		if ( st == false)
			updatesect(dcap, disk)
		for (i=1; i<=4; i++) {
			document.getElementById("keep_" + disk + i).checked = !st;
			document.getElementById("keep_" + disk + i).disabled = st;

			document.getElementById("start_" + disk + i).disabled = !st;
			document.getElementById("len_" + disk + i).disabled = !st;
			document.getElementById("cap_" + disk + i).disabled = true;
			document.getElementById("type_" + disk + i).disabled = !st;
			document.getElementById("adv_id").value = (st == true ? "Basic" : "Advanced")
		}
	}

	function check_adv(dcap, disk, pn) {
		free = dcap
		ostart = 0
		msg = ""
		for (i=1; i<=4; i++) {
			start = parseInt(document.getElementById("start_" + disk + i).value)
			len = parseInt(document.getElementById("len_" + disk + i).value)
			type = document.getElementById("type_" + disk + i).selectedIndex

			rem = start % 8
			if (rem != 0)
				msg += "Start of partition " + i + " is not 4k aligned (by " + rem + " sectors)" + '\n'
			rem = len % 8
			if (rem != 0)
				msg += "Lenght of partition " + i + " is not 4k aligned (by " + rem + " sectors)" + '\n'

			off = ostart - start 
			if (off > 0 && type != 0)
				msg += "Partition " + i + " starts " + off + " sectors within partition " + (i-1) + '\n'
			ostart = start + len

			document.getElementById("cap_" + disk + i).value =  Math.round(len * 512 / 1e6)/1000;
			free -= len;
		}
		if (free < 0)
			msg += "More sectors allocated than available on disk."

		document.getElementById("free_id").value = Math.round(free * 512 / 1e6)/1000;

		if (msg.length > 0)
			alert(msg)

	}

	// update sectors view and free available space when entering partition size in GB
	function updatesect(dcap, dsk) {
		free = dcap;
		for (i=1; i<=4; i++) {
			prev = "" + dsk + (i - 1)
			if (i == 1)
				pstart = 64
			else {
				pstart = parseInt(document.getElementById("start_" + prev).value) +
					parseInt(document.getElementById("len_" + prev).value);
			}

			if (document.getElementById("keep_" + dsk + i).checked == false) {
				document.getElementById("start_" + dsk + i).value = pstart;
				nsect = document.getElementById("cap_" + dsk + i).value * 1e9 / 512;
				nsect -= nsect % 8
				document.getElementById("len_" + dsk + i).value = nsect;
				if (nsect == 0)
					document.getElementById("type_" + dsk + i).selectedIndex = 0;
			}
			free -= document.getElementById("len_" + dsk + i).value;
		}
		document.getElementById("free_id").value = Math.round(free * 512 / 1e6)/1000;
	}

	// partition submit
	function psubmit(diskcap, bay, free) {
		if (document.getElementById("free_id").value < 0 ) {
			alert("The sum of the partitions size is greater than the disk capacity.\n\
Decrease the size of some partitions and retry.")
			return false
		}
		
		return confirm("Partitioning the " + diskcap + " " + bay + " disk can make all its data inacessible.\n\nContinue?")
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
	for i in $disks; do
		dsk=$i
		break
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

	disk_details $disk

	chkd=""	
	if test "$i" = "$dsk"; then chkd="checked"; fi

	cat<<-EOF
		<tr>
		<td><input type=radio $chkd name=disk value=$disk onchange="reopen('$disk')"></td>
		<td>$dbay</td>
		<td align=center>$disk</td>
		<td align=right>$dcap</td>
		<td>$dmod</td>
		<td><select id=op_$disk name=op_$disk onChange="opsubmit('$disk','$dbay','$dcap')">
			<option>Operation</option>
			<option>Erase</option>
			<option>Save</option>
			<option>Load</option>
		</select></td>
		<td><select id=cp_$disk name=cp_$disk onChange="msubmit('$disk','$dbay', '$dcap')">$opt_disks</select></td>
		</tr>
	EOF
done

echo "<input type=hidden name=cp_from>"
echo "</table></fieldset><br>"	

ddsk=$(basename $dsk)
#rawcap=$(expr $(sfdisk -s $dsk) \* 2) # sectors
rawcap=$(cat /sys/block/$dsk/size)

disk_details $ddsk

cat<<-EOF
	<fieldset>
	<legend><strong>Partition $dbay disk, $dcap, $dmod </strong></legend>
	<table>
	<tr align=center>
	<th> Keep </th>
	<th> Dev </th>
	<th><span $(ttip tt_pstart)> Start sector </span></th>
	<th><span $(ttip tt_plen)> Lenght </span> </th>
	<th><span $(ttip tt_psize)> Size (GB)</span></th>
	<th> Type </th>
	</tr>
EOF

fout=$(sfdisk -luS $dsk | tr '*' ' ') # *: the boot flag...

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
		/'$ppart'/{printf "id=\"%s\" type=\"%s\"; cap=%.3f; start=%d; len=%d;", \
		$5, substr($0, index($0,$6)), $4*512/1e9, $2, $4}')

	used=$(expr $used + $len)

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
		onclick="keeppart('$ppart')" $(ttip tt_keep)></td>
	<td>$ppart</td>
	<td><input type=text disabled size=10 id=start_$ppart name=start_$ppart value=$start
		onchange="check_adv('$rawcap', '$ddsk', '$pl')"  $(ttip tt_pstart)></td>
	<td><input type=text disabled size=10 id=len_$ppart name=len_$ppart value=$len
		onchange="check_adv('$rawcap', '$ddsk', '$pl')" $(ttip tt_plen)></td>
	<td><input type=text $keepdis size=6 id=cap_$ppart name=cap_$ppart 
		value=$cap onclick="updatesect('$rawcap', '$ddsk')" onmouseout="updatesect('$rawcap', '$ddsk')" $(ttip tt_psize)></td>
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

free=$(awk 'BEGIN {printf "%.3f", ('$rawcap' - '$used') * 512/1e9}')

cat<<-EOF
	<tr><td colspan=3></td>
	<td align=right>Free: </td>
	<td><input type=text readonly id="free_id" size=6 value="$free" $(ttip tt_free)></td>
	</tr>
	<tr><td align=center colspan=2><input type=submit name=$ddsk value=Partition
		onclick="return psubmit('$dcap', '$dbay', '$free')"></td>
	<td><input type=button id=adv_id value=Advanced onclick="return advanced('$rawcap','$ddsk')"></td>
	</tr>
	</table></fieldset><br>
	</form></body></html>
EOF
