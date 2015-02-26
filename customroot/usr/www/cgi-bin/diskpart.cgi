#!/bin/sh

. common.sh
check_cookie
write_header "Disk Partitioner" "document.diskp.reset()"

has_disks

mktt tt_keep "If <strong>never</strong> unchecked, no changes will be made to this partition."
mktt tt_psize "Partition size. Rounding can occur."
mktt tt_pstart "Partition start sector."
mktt tt_plen "Partition length, in sectors."
mktt tt_free "Free disk space. Rounding can occur."

cat<<EOF
	<script type="text/javascript">
	// Erase, Save, Load and Convert operations
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

		else if (op == "Conv_MBR") {
			ret = confirm('You are going to convert the ' + cap + ' ' + bay + ' disk\
partition table to the MBR format.\n\Adjustments might be necessary afterwards.\n\nContinue?') 
		}

		else if (op == "Conv_GPT") {
			ret = confirm('You are going to convert the ' + cap + ' ' + bay + ' disk\
partition table to the GPT format.\n\Adjustments might be necessary afterwards.\n\nContinue?') 
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
		if (topart == "CopyTo") {
			alert("Select a destination disk.")
			obj.selectedIndex = 0
		} else {
			ret = confirm("The partition table of the " + frompart + " disk will be copied" + '\n' + "to the " + topart + " disk, " + \
"making all " +  topart + " disk data inacessible." + '\n' + "Success depends on disk sizes." + '\n' + '\n' + "Continue?")
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
		}
		document.getElementById("adv_id").value = (st == true ? "Basic" : "Advanced")
		document.getElementById("adv_hid").value = (st == false ? "Basic" : "Advanced")
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
				msg += "Length of partition " + i + " is not 4k aligned (by " + rem + " sectors)" + '\n'

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
		msg = ""
		prev_end = 64
		for (i=1; i<=4; i++) {
			if (document.getElementById("keep_" + dsk + i).checked == false) {
				start = prev_end
				nsect = document.getElementById("cap_" + dsk + i).value * 1e9 / 512
				nsect -= nsect % 8
				document.getElementById("start_" + dsk + i).value = start
				document.getElementById("len_" + dsk + i).value = nsect
			} else {
				start = parseInt(document.getElementById("start_" + dsk + i).value)
				nsect = parseInt(document.getElementById("len_" + dsk + i).value)
				if (prev_end > start) {
					pmaxsize = Math.round((prev_end - start) * 512 / 1e6)/1000
					msg += "Partition " + (i - 1) + " capacity exceeded by " + pmaxsize + " GB" + '\n'
				}
			}
			prev_end = start + nsect
			free -= document.getElementById("len_" + dsk + i).value;
		}
		if (prev_end > dcap) {
			pmaxsize = Math.round((prev_end - dcap) * 512 / 1e6)/1000
			msg += "Partition 4 capacity exceeded by " + pmaxsize + " GB" + '\n'
		}

		cfree = Math.round(free * 512 / 1e6)/1000;
		document.getElementById("free_id").value = cfree;
		if (cfree < 0)
			msg += '\n' + "Disk capacity exceeded by " + (-cfree) + " GB"
 
		if (msg.length > 0)
			alert(msg)
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
	parse_qstring
	dsk="/dev/$(httpd -d "$disk")"
else
	for i in $disks; do
		dsk=$i
		break
	done
fi

ntfs_avail="disabled"
if test -f /usr/sbin/mkntfs; then
	ntfs_avail=""
fi

cat<<EOF
	<fieldset>
	<legend>Select the disk you want to partition</legend>
	<table>
	<tr>
	<th>Partition</th>
	<th>Bay</th>
	<th>Device</th>
	<th>Capacity</th>
	<th>Model</th>
	<th class="highcol" colspan=2>Partition Table</th>
	</tr>
EOF

opt_disks="$(for i in $disks; do echo "<option>$(basename $i)</option>"; done)"
 
for i in $disks; do
	disk=$(basename $i)

	disk_details $disk

	optd=$(echo $opt_disks | sed 's|<option>'$disk'</option>||')

	conv_gpt_dis=""; conv_mbr_dis=""
	if fdisk -lu $i 2> /dev/null | grep -q "Found valid GPT with protective MBR; using GPT"; then
		conv_gpt_dis="disabled"
	else
		conv_mbr_dis="disabled"
	fi
	
	chkd=""	
	if test "$i" = "$dsk"; then chkd="checked"; fi

	cat<<EOF
		<tr>
		<td><input type=radio $chkd name=disk value="$disk" onchange="reopen('$disk')"></td>
		<td>$dbay</td>
		<td align=center>$disk</td>
		<td align=right>$dcap</td>
		<td>$dmod</td>
		<td class="highcol"><select id=op_$disk name=op_$disk onChange="opsubmit('$disk','$dbay','$dcap')">
			<option>Operation</option>
			<option>Erase</option>
			<option>Save</option>
			<option>Load</option>
			<option $conv_mbr_dis value=Conv_MBR>Convert to MBR</option>
			<option $conv_gpt_dis value=Conv_GPT>Convert to GPT</option>
		</select></td>
		<td class="highcol"><select id=cp_$disk name=cp_$disk onChange="msubmit('$disk','$dbay', '$dcap')"><option>CopyTo</option>$optd</select></td>
		</tr>
EOF
done

cat<<EOF
	</table></fieldset>
	<input type=hidden name=cp_from>
EOF

ddsk=$(basename $dsk)
rawcap=$(cat /sys/block/$ddsk/size) # sectors
#rawcap=3907024065 # 2 TB 
#rawcap=5860536096 # 3 TB

disk_details $ddsk

fout=$(fdisk -lu $dsk 2> /dev/null | tr '*' ' ') # *: the boot flag...

npart=4
keepchk="checked"
keepdis="disabled"
windd_dis="disabled"
in_use="MBR"
if $(echo $fout | grep -q "Found valid GPT with protective MBR; using GPT"); then
	in_use="GPT"
	windd_dis=""; ntfsd="disabled"; vfatd="disabled"
fi

swapneeded=""
if test "$dbay" != "usb"; then
	swapneeded="<p>Every internal disk must have a swap partition as its first partition, 0.5GB is generally enough.</p>"
fi

cat<<EOF
	<fieldset>
	<legend>Partition $dbay disk, $dcap, $dmod </legend>
	<p>Using <strong>$in_use</strong> partitioning.</p>
	$swapneeded
	<input type=hidden name=in_use value="$in_use">
	<table>
	<tr align=center>
	<th>Keep</th>
	<th>Dev</th>
	<th><span $(ttip tt_pstart)>Start sector</span></th>
	<th><span $(ttip tt_plen)>Length</span> </th>
	<th><span $(ttip tt_psize)>Size (GB)</span></th>
	<th>Type</th>
	</tr>
EOF

if $(echo $fout | grep -q "doesn't contain a valid partition table"); then
	fout="${dsk}1          0       -       0          0    0  Empty
${dsk}2          0       -       0          0    0  Empty
${dsk}3          0       -       0          0    0  Empty
${dsk}4          0       -       0          0    0  Empty"
keepchk=""
keepdis=""
fi

used=0
for pl in $(seq 1 $npart); do
	part=${dsk}$pl
	ppart=$(basename $part)

	id=""; type=""; cap=""; start=""; len="";
	eval $(echo "$fout" | awk '
		/'$ppart'/{len = $3 - $2 ; if (len > 0) len += 1; printf "id=\"%s\" type=\"%s\"; cap=%.3f; start=%.0f; len=%.0f;", \
		$5, substr($0, index($0,$6)), len * 512/1e9, $2, len}')

	if test -n "$len"; then
		used=$(expr $used + $len)
	fi

	emptys=""; swaps=""; linuxs=""; lvms=""; raids="";
	vfats=""; ntfss=""; extendeds=""; GPTs=""; windds=""
	case $id in
		0) emptys="selected" ;;
		82|8200) swaps="selected" ;;
		83|8300) linuxs="selected" ;;
		8e|8e00) lvms="selected" ;;
		5|f|85) extendeds="selected" ;;
		fd|da|fd00) raids="selected"	;;
		b|c) vfats="selected" ;;
		7) ntfss="selected" ;;
		ee) GPTs="selected";;
		0700) windds="selected";;
	esac

	cat<<EOF
	<tr>
	<td align=center><input type="checkbox" $extendeddis $keepchk id="keep_$ppart" name="keep_$ppart" value="yes" 
		onclick="keeppart('$ppart')" $(ttip tt_keep)></td>
	<td>$ppart</td>
	<td><input type=text disabled size=10 id=start_$ppart name=start_$ppart value="$start"
		onchange="check_adv('$rawcap', '$ddsk', '$pl')"  $(ttip tt_pstart)></td>
	<td><input type=text disabled size=10 id=len_$ppart name=len_$ppart value="$len"
		onchange="check_adv('$rawcap', '$ddsk', '$pl')" $(ttip tt_plen)></td>
	<td><input type=text $keepdis size=6 id=cap_$ppart name=cap_$ppart 
		value="$cap" onkeyup="updatesect('$rawcap', '$ddsk')" $(ttip tt_psize)></td>
	<td><select $keepdis id=type_$ppart name=type_$ppart>
	<option $emptys>empty</option>
	<option $raids>RAID</option>
	<option $swaps>swap</option>
	<option $linuxs>linux</option>
	<option $lvms>LVM</option>
	<option $vfatd $vfats>vfat</option>
	<option $ntfsd $ntfss $ntfs_avail>ntfs</option>
	<option $extendeds disabled>extended</option>
	<option $GPTs disabled>GPT</option>
	<option $windds $windd_dis>Windows Data</option>
	</select></td>
	</tr>
EOF

done 

free=$(awk 'BEGIN {printf "%.3f", ('$rawcap' - '$used') * 512/1e9}')

cat<<EOF
	<tr><td colspan=4 align=right>Free:</td>
	<td colspan=2><input type=text readonly id="free_id" size=6 value="$free" $(ttip tt_free)></td>
	</tr></table></fieldset>

	<input type=submit name=$ddsk value=Partition onclick="return psubmit('$dcap', '$dbay', '$free')">
	<input type=button id=adv_id name=adv_bt value="Advanced" onclick="return advanced('$rawcap','$ddsk')">
	<input type=hidden id=adv_hid name=adv_fl value="Basic">
	</form></body></html>
EOF
