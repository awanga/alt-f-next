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

	// update free space, check for NaNs, display error messages
	function check_NaN(dcap, msg) {
		document.getElementById("free_id").value = Math.round(dcap * 512 / 1e6)/1000;
		if (dcap < 0 || isNaN(dcap))
			document.getElementById("free_id").style.color = "red"
		else
			document.getElementById("free_id").style.color = ""

		if (msg.length > 0)
			alert(msg)
	}

	// update size view and free available space when in advance mode
	function check_adv(dcap, disk, pn) {
		ostart = 0
		msg = ""
		for (i=1; i<=4; i++) {
			start = Number(document.getElementById("start_" + disk + i).value)
			len = Number(document.getElementById("len_" + disk + i).value)

			if (isNaN(start))
				msg += "Start of partition " + i + " is not a number" + '\n'
			if (isNaN(len))
				msg += "End of partition " + i + " is not a number" + '\n'

			rem = start % 8
			if (rem != 0)
				msg += "Start of partition " + i + " is not 4k aligned (by " + rem + " sectors)" + '\n'
			rem = len % 8
			if (rem != 0)
				msg += "Length of partition " + i + " is not 4k aligned (by " + rem + " sectors)" + '\n'

			document.getElementById("cap_" + disk + i).value =  Math.round(len * 512 / 1e6)/1000;
			dcap -= len;
		}
		check_NaN(dcap, msg)
	}

	// update sectors view and free available space when entering partition size in GB
	function updatesect(dcap, dsk, pn) {
		var part = [], free = [], msg = "", curr = 64

		// get displayed partition table
		for (i=1; i<=4; i++) {
			cap = Number(document.getElementById("cap_" + dsk + i).value)
			if (isNaN(cap))
				msg += "Size of partition " + i + " is not a number" + '\n'
			part.push({
				pn: i,
				chk: document.getElementById("keep_" + dsk + i).checked,
				start: Number(document.getElementById("start_" + dsk + i).value),
				len: Number(document.getElementById("len_" + dsk + i).value),
				cap: cap})
			}

		// sort by increasing start sectors
		part.sort(function(a,b){ return a.start - b.start})
		for (i in part)
			console.log("part: " + part[i].pn + " " + part[i].chk + " " + part[i].start + " " + part[i].len + " " + (part[i].start + part[i].len) + " " + part[i].cap)

		// find free areas bettwin checked partitions
		for (i in part) {
			if (part[i].chk == true) {
				ps = part[i].start
				pl = part[i].len
				if (pl == 0)
					continue
				fs = curr
				fl = ps - fs
				free.push({start: fs, len: fl})
				curr = ps + pl
				rem = curr % 8
				if (rem != 0)
					curr += 8 - rem
			}
		}
		// last free area until the disk ends
		if (curr < dcap) {
			var t = {start: curr, len: dcap - curr}
			free.push(t)
		}
		for (i in free)
			console.log(i + " free: " + free[i].start + " " + free[i].len + " " + (free[i].start + free[i].len))

		// sort by increasing part sectors
		part.sort(function(a,b){ return a.pn - b.pn})

		// fit partition to first free area
		for (i in part) {
			found = 0
			if (part[i].chk == true) {
				st = part[i].start
				nsect = part[i].len
			} else {
				nsect = part[i].cap * 1e9 / 512
				nsect -= nsect % 8
				if (nsect == 0) {
					st = 0 
				} else {
					for (j in free) {
						if (free[j].len >= nsect) {
							st = free[j].start
							free[j].start += nsect
							free[j].len -= nsect
							found = 1
							break	
						}
					}
					if (found == 0)
						msg += "No continuos free disk space for partition " + part[i].pn 
				}
			}
			p = part[i].pn
			document.getElementById("start_" + dsk + p).value = st
			document.getElementById("len_" + dsk + p).value = nsect
			document.getElementById("cap_" + dsk + p).value = Math.round(nsect * 512 / 1e6)/1000
			//document.getElementById("cap_" + dsk + p).value = (nsect * 512 / 1e9).toFixed(3)
			dcap -= nsect;
		}
		check_NaN(dcap, msg)
	}

	// disable start/len when submission is canceled
	function re_set(disk, pst) {
		for (i=0; i<=4; i++) {
			if (pst[i] == true) {
				document.getElementById("start_" + disk + i).disabled = true;
				document.getElementById("len_" + disk + i).disabled = true;
			}
		}
	}

	// partition submit
	function psubmit(diskcap, disk, bay, rawcap) {
		var start = [], len = [], end = [], type = [], pst = [];
		emsg = "";
		for (i=1; i<=4; i++) {
			// _proc.cgi has to read start and len, set by update sectors on Basic mode
			// but if user cancels the submission, previous state needs to be set
			pst[i] = document.getElementById("start_" + disk + i).disabled
			document.getElementById("start_" + disk + i).disabled = false;
			document.getElementById("len_" + disk + i).disabled = false;

			start[i] = Number(document.getElementById("start_" + disk + i).value)
			len[i] = Number(document.getElementById("len_" + disk + i).value)
			end[i] = start[i] + len[i]
			type[i] = document.getElementById("type_" + disk + i).selectedIndex
		}

		for (i=1; i<=4; i++) {
			if (isNaN(start[i])) 
				emsg += "Start of partition " + i + " is not a number" + '\n'
			if (isNaN(len[i]))
				emsg += "Length of partition " + i + " is not a number" + '\n'

			rawcap -= len[i]
			rem = start[i] % 8
			if (rem != 0)
				emsg += "Start of partition " + i + " is not 4K aligned (by " + rem + " sectors)" + '\n'

			rem = len[i] % 8
			if (rem != 0)
				emsg += "Length of partition " + i + " is not 4K aligned (by " + rem + " sectors)" + '\n'

			for (j=1; j<=4; j++) {
				if (i == j) continue
				if (start[j] == undefined || len[j] == undefined) continue

				if (start[i] >= start[j] && start[i] < end[j])
					emsg += "Start of partition " + i + " conflicts with partition " + j + '\n'
				if (end[i] > start[j] && end[i] < end[j])
					emsg += "End of partition " + i + " conflicts with partition " + j + '\n'
			}
		}

		dfree = Math.round(rawcap * 512 / 1e6)/1000;
		document.getElementById("free_id").value = dfree;

		if (dfree < 0)
			emsg += '\n' + "Disk capacity exceeded by " + -dfree + " GB"

		if (emsg.length != 0) {
			re_set(disk, pst)
			alert(emsg)
			return false;
		}
		
		if (! confirm("Partitioning the " + diskcap + " " + bay + " disk can make all its data inacessible.\n\nContinue?")) {
			re_set(disk, pst)
			return false
		}
		return true
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

TWOTB=4294967296 # 2.2TB
# FIXME: the sh 'let'/'$((' range is limited to +/-2TB, a signed 32 bits int, use 'expr' !

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
	
	if test $(cat /sys/block/$disk/size) -gt $TWOTB; then
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
rawcap=$(cat /sys/block/$ddsk/size) # 512 bytes sectors
sectsz=$(cat /sys/block/$ddsk/queue/logical_block_size)
#sectsz=4096
disk_details $ddsk

if test "$sectsz" != "512"; then
	bigsectsz="<p class=\"error\">Disk has 4KB logical sector size, use the command line to partition it.</p>"
	partdis="disabled"
fi

swapneeded=""
if test "$dbay" != "usb"; then
	swapneeded="<p>Every internal disk must have a swap partition as its first partition, 0.5GB per 2TB disk is generally enough.</p>"
fi

fout=$(fdisk -lu $dsk 2> /dev/null | tr '*' ' ') # *: the boot flag...

npart=4
keepchk="checked"
keepdis="disabled"
windd_dis="disabled"

if echo $fout | grep -q "doesn't contain a valid partition table"; then
	if test $rawcap -lt $TWOTB; then
		in_use="MBR"
	else
		in_use="GPT"
	fi

	fout="${dsk}1          0       -       0          0    0  Empty
${dsk}2          0       -       0          0    0  Empty
${dsk}3          0       -       0          0    0  Empty
${dsk}4          0       -       0          0    0  Empty"
	keepchk=""
	keepdis=""

elif echo $fout | grep -q "Found valid GPT with protective MBR; using GPT"; then
	in_use="GPT"
	windd_dis=""
	ntfsd="disabled"
	vfatd="disabled"
else
	in_use="MBR"
fi

cat<<EOF
	<fieldset>
	<legend>Partition $dbay disk, $dcap, $dmod </legend>
	$bigsectsz
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
	<!--td><input type=text $keepdis size=6 id=cap_$ppart name=cap_$ppart 
		value="$cap" onkeyup="updatesect('$rawcap', '$ddsk', '$pl')" $(ttip tt_psize)></td-->
	<td><input type=text $keepdis size=6 id=cap_$ppart name=cap_$ppart 
		value="$cap" onchange="updatesect('$rawcap', '$ddsk', '$pl')" $(ttip tt_psize)></td>
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

	<input type=submit name=$ddsk $partdis value=Partition onclick="return psubmit('$dcap', '$ddsk', '$bay', '$rawcap')">
	<input type=button id=adv_id $partdis name=adv_bt value="Advanced" onclick="return advanced('$rawcap','$ddsk')">
	<input type=hidden id=adv_hid name=adv_fl value="Basic">
	</form></body></html>
EOF
