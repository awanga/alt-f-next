#!/bin/sh

. common.sh

check_cookie
write_header "RAID Creation and Maintenance" "document.diskr.reset()"

isflashed
flashed=$?

cat<<-EOF
	<script type="text/javascript">
	function msubmit(id, part) {
		obj = document.getElementById(id)
		opi = obj.selectedIndex
		op = obj.options[opi].value

		res = false
		if (opi == 0)
			return false;

		if (op == "Remove_bitmap") // write intent bitmap
			res = confirm("Removing the Write Intent Bitmap makes resyncing much slower\n\
with a slight increase in performance.\n\n\
Continue?")

		else if (op == "Create_bitmap") // write intent bitmap
			res = confirm("Creating a Write Intent Bitmap makes resyncing much faster\n\
at the expense of a small performance degradation.\n\n\
Continue?")	

		else if (op == "Verify" || op == "Repair" || op == "Details" || op == "Examine_part")
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

		else if (op == "Destroy_raid") // raid to release its components
			res = confirm("Destroying a RAID will make all data it contains inaccessible\n\
and will make its components available to other RAID arrays.\n\n\
However, for RAID1, the data it contains will be available duplicated on\n\
each component, which can be used latter as a \"standard\" filesystem.\n\nContinue?")

		else if (op == "Add_part" || op == "Remove_part" || op == "Fail_part" || op == "Clear_part") {
			if (document.getElementById("rdev_" + part).selectedIndex == 0) {
				alert("Select a Partition first.")
				obj.selectedIndex = 0
				return false
			}
			if (op == "Add_part")
				res = confirm("Add a partition to " + part + " if you want to add a spare component\n\
or are replacing a faulty and already removed component.\n\nContinue?")
			else if (op == "Remove_part")
				res = confirm("Removing a partition from " + part + " can only\n\
be done if it is a spare or failed partition.\n\nContinue?")
			else if (op == "Fail_part")
				res = confirm("Marking a partition as failed from " + part + " makes it loose\n\
its redundancy or even stop the array.\n\nContinue?")
			else if (op == "Clear_part")
				res = confirm("Clearing a RAID partition makes it loose its RAID information.\n\
It must have already been removed from the array.\n\nContinue?")
		}

		if (res == true)
			document.getElementById("diskr").submit();
		else
			obj.selectedIndex=0
	}

	function csubmit(arg, notflashed) {

		obj = document.diskr.level
		level = obj.options[obj.selectedIndex].value

		if (arg == "submit") {
			comp1 = document.diskr.comp1.value;
			comp2 = document.diskr.comp2.value;
			comp3 = document.diskr.comp3.value;

			if ((comp1 != "none" && comp2 != "none" && \
					comp1.substr(0,3) == comp2.substr(0,3)) || \
				(comp1 != "none" && comp3 != "none" && \
					comp1.substr(0,3) == comp3.substr(0,3)) || \
				(comp2 != "none" && comp3 != "none" && 	
					comp2.substr(0,3) == comp3.substr(0,3))) {
					st = confirm ("Warning: RAID components should be on different disks.\n\
If you continue, performance will be worse than that of a single disk.\n\nContinue?")
					if (st == false)
						return false
			}

			ret = false
			if (level == "raid5") {
				if (notflashed == 1) {
					if (! confirm("Your box is not flashed and RAID5 is not recognized by the stock firmware." + '\n' + "Proceed anyway?"))
						return false
				}
				if (comp1 == comp2 || comp1 == comp3 || comp2 == comp3)
					alert("All componentes must be different.");
				else if (comp3 == "none")
					ret = confirm("Your RAID5 array will be started in degraded mode.\n\
Add a component as soon as possible.\n\nContinue?")
				else ret = true
			} else if (level == "raid1") {
				if (comp1 != "none" && comp2 == "none" && comp3 == "none")
					ret = confirm("Your RAID1 array will be started in degraded mode.\n\
Add a component as soon as possible.\n\nContinue?")
				else if (comp1 == comp2 || comp1 == comp3 || comp2 == comp3)
					alert("All componentes must be different.");
				else ret = true
			}
			else if (level == "linear" || level == "raid0") {
				if (comp1 == "none" || comp2 == "none")
					alert("For JBD or RAID0 you have to select two components.")
				else if (comp1 == comp2)
					alert("All componentes must be different.");
				else ret = true
			}

			return ret
		}

		document.diskr.comp3.disabled = false

		if (level == "raid0") {
			document.diskr.comp3.disabled = true
			document.getElementById("spare_hd").innerHTML = ""
		}
		else if (level == "raid1")
			document.getElementById("spare_hd").innerHTML = "Spare"
		else if (level == "linear" || level == "raid5") {
			document.getElementById("spare_hd").innerHTML = "Component 3"
		}

		return true
	}
	</script>
EOF

has_disks

# THIS IS RIGHT!
p1=$(fdisk -l /dev/sd? 2>/dev/null | awk 'substr($1,1,5) == "/dev/" && ($5 == "da" || $5 == "fd" || $5 == "fd00") {
	print substr($1, 6)}')
p2=$(blkid -t TYPE="mdraid" | awk '{print substr($1, 6, 4)}')
raidp=$(echo -e "$p1\n$p2" | sort -u)

if test -z "$raidp"; then
	echo "<h4>No partitions of type RAID found, use the Disk Partitioner to create RAID partitions.</h4>"
	exit 0
fi

pairs="<option>none</option>"
for i in $raidp; do
	cap="$(awk '{printf "%.0f", $0*512/1e9}' /sys/block/${i:0:3}/$i/size)"
	pairs="$pairs <option value=\"$i\">$i ${cap}GB</option>"
done

# THIS IS RIGHT! first non-existing md device
#curdev=$(mdadm --examine --scan | awk '/ARRAY/{ print substr($2, match($2, "md"))}')
# for metadata 1.2 mdadm reports /dev/md/0, /dev/md/1... which are simlinks to /dev/md0, /dev/md1...
curdev=$(for i in $(mdadm --examine --scan | awk '/ARRAY/{ print substr($2, match($2, "md"))}'); do
	if test -h /dev/$i; then
		if a=$(readlink -f /dev/$i); then basename $a; fi
	else
		echo $i
	fi
done)

for dev in $(seq 0 9); do
	if ! echo $curdev | grep -q md$dev; then break; fi
done

cat<<-EOF
	<form id="diskr" name="diskr" action="/cgi-bin/raid_proc.cgi" method="post">

	<fieldset>
	<legend>RAID Creation</legend>
	<table>
	<tr>
	<th>Dev.</th>
	<th>Type</th>
	<th>Component 1</th>
	<th>Component 2</th>
	<th id="spare_hd">Spare</th>
	</tr>

	<tr align=center>
	<td>md$dev</td>
	<td><select name="level" onchange="return csubmit()">
		<option value="linear">JBD</option>
		<option value="raid0">Raid 0</option>
		<option selected value="raid1">Raid 1</option>
		<option value="raid5">Raid 5</option>
		</select></td>
	<td><select name="comp1">$pairs</select></td>
	<td><select name="comp2">$pairs</select></td>
	<td><select name="comp3">$pairs</select></td>
	</tr></table>
	<br><input type=submit name=md$dev value=Create onclick="return csubmit('submit', '$flashed')">
	</fieldset>
EOF

if mdadm --examine --brief /dev/sd?? 2> /dev/null | grep -q ARRAY; then
	cat<<-EOF
		<fieldset><legend>RAID Maintenance</legend>
		<table>
		<tr>
		<th>Dev.</th> 
		<th>Capacity</th>
		<th>Level</th>
		<th>Components</th>
		<th></th>
		<th>Array</th>
		<th>RAID Operations</th>
		<th class="highcol" colspan=2>Component Operations</th>
 		</tr>
	EOF

	raid_devs="<option value=none>Partition</option>"

	for j in $raidp; do
		cap="$(awk '{printf "%.0f", $0*512/1e9}' /sys/block/${j:0:3}/$j/size)"
		raid_devs="$raid_devs<option value=\"$j\">$j ${cap}GB</option>"
	done

	if ls /dev/md? >& /dev/null; then
		for mdev in $curdev; do
			if ! test -f /sys/block/$mdev/md/array_state; then continue; fi

			state=$(cat /sys/block/$mdev/md/array_state)
			type=$(cat /sys/block/$mdev/md/level)
			pcap=$(awk '/'$mdev'/{printf "%.1f GB", $3/1048576}' /proc/partitions)

			act="Stop"
			destroy_dis=""
			if test "$state" = "clear"; then
				act="Start"
				destroy_dis="disabled"
			fi

			devs=""
			for j in $(ls /sys/block/$mdev/slaves); do
				if test $(cat /sys/block/$mdev/md/dev-$j/state) = "faulty"; then
					devs="$devs <span class=\"red\">$j</span>"
				elif test $(cat /sys/block/$mdev/md/dev-$j/state) = "spare"; then
					devs="$devs <span class=\"green\">$j</span>"
				else
					devs="$devs $j"
				fi
			done
	
			otype=$type
			if test "$(cat /sys/block/$mdev/md/degraded 2>/dev/null )" = 1; then
				otype="<span class=\"red\">$type</span>"
			fi
	
			cat<<-EOF
				<tr>
				<td align=left>$mdev</td> 
				<td>$pcap</td>
				<td>$otype</td>
				<td>$devs</td>
			EOF

			remops=""
			if ! test "$type" = "raid1" -o "$type" = "raid5"; then
				remops="disabled"
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
				abort=""
				if test "$action" = "check" -o "$action" = "repair"; then
					abort="<input type=submit name=$mdev value=\"Abort\">"
				fi
				cat<<-EOF
					<td><span class="red"> ${action}ing </span>
					$abort</td>
					<td colspan="3"><input type=submit name=$mdev value="Stop"</td>
					</tr>
				EOF
			else
				cat<<-EOF
					<td></td>
					<td><input type=submit name=$mdev value=$act></td>		
					<td><select id="raidop_$mdev" name="$mdev" onChange="msubmit('raidop_$mdev', '$mdev')">
						<option>Operation</option>
						<option $remops value="${bitmap}_bitmap">$bitmap Bitmap</option>
						<option $remops>Verify</option>
						<option $remops>Repair</option>
						<option $remops value="Enlarge_raid">Enlarge</option>
						<option $remops value="Shrink_raid">Shrink</option>
						<option $destroy_dis value="Destroy_raid">Destroy</option>
						<option>Details</option>
					</select></td>
				EOF

				if test -n "$remops"; then continue; fi

				cat<<-EOF
					<td class="highcol"><select id=rdev_$mdev name=rdev_$mdev>$raid_devs</select></td>
					<td class="highcol"><select id=rops_$mdev name=$mdev onChange="msubmit('rops_$mdev', '$mdev')">
						<option value=none>Operation</option>
						<option value=Fail_part>Fail</option>
						<option value=Remove_part>Remove</option>
						<option value=Add_part>Add</option>
						<option value=Examine_part>Examine</option>
						<option value=Clear_part>Clear</option>
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
			<td></td>
			<td><input type=submit name=$rdev value="Start"></td>
			</tr>
		EOF
	done
fi

cat<<-EOF
	</table></fieldset>
	</form></body></html>
EOF
