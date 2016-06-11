#!/bin/sh

. common.sh
check_cookie
write_header "Disk Wizard"

has_disks

cat<<-EOF
	<script type="text/javascript">
	function validate(ndisks) {
		for (var i = 0; i < document.wizf.wish_part.length; i++) {
			if (document.wizf.wish_part[i].checked=="1")
				ptype=document.wizf.wish_part[i].value
		}

		for (var i = 0; i < document.wizf.wish_fs.length; i++) {
			if (document.wizf.wish_fs[i].checked=="1")
				fstype=document.wizf.wish_fs[i].value
		}

		t=0;
		for (var i = 1; i <= ndisks; i++) {
			if (document.getElementById("disk_" + i).checked == true)
				t++;
		}
		ndisks = t;

		if (ndisks == 1 && (ptype == "raid0" || ptype == "jbd")) {
			alert("You need at least two disks to create a " + ptype + " RAID array")
			return false
		}
		if (ndisks == 1 && ptype == "raid5") {
			alert("You need at least two disks to create a " + ptype + " RAID array")
			return false
		}
		if ((ndisks == 1 && ptype == "raid1") || (ndisks == 2 && ptype == "raid5"))
			return confirm("Your " + ptype + " RAID array will be started in degraded mode.\n\
You should add another disk as soon as possible.\n\n\
Your " + ndisks + " disk(s) will be partitioned as " + ptype + " and\n\
formated with " + fstype + " and all its content will be lost.\n\n\
Continue?")
		if (ptype != "notouch")
			return confirm("Your " + ndisks + " disk(s) will be partitioned as " + ptype + "\n\
and formated with " + fstype + " and all its content will be lost.\n\n\
Continue?")
	}
	</script>
	<form name=wizf action="/cgi-bin/diskwiz_proc.cgi" method="post">	
	<fieldset>
	<legend>Select the disks you want to format</legend>
	<table><tr>
	<th>Format</th>
	<th>Bay</th>
	<th>Device</th>
	<th>Capacity</th>
	<th>Model</th>
	</tr>
EOF

j=1;
for i in $disks; do
	disk=$(basename $i)
	disk_details $disk
	sectsz=$(cat /sys/block/$disk/queue/logical_block_size)
	#sectsz=4096

	wizdisk="checked"
	if test "$sectsz" != "512"; then
		bigsectsz="<span class=\"error\">Disk has 4KB logical sector size, not yet supported.</span>"
		wizdisk="disabled"
	fi

	if test "$(cat /sys/block/${disk}/size)" -gt 3907024065; then
		huge_disk="yes"
	fi

	cat<<-EOF
		<tr>
		<td align=center><input type=checkbox $wizdisk id="disk_$j" name="disk_$j" value="$disk"></td>
		<td>$dbay</td>
		<td align=center>$disk</td>
		<td align=right>$dcap</td>
		<td>$dmod</td>
		<td>$bigsectsz</td>
		</tr>
	EOF
	j=$((j+1))
done
echo "</table></fieldset><input type=hidden name=num_disks value=$((j-1))>"	

nusb="$(cat /etc/bay | grep =usb | wc -l)"
if test  "$nusb" -ge 2; then
	echo '<center><h4 class="blue">For performance reasons you should have no more than one external USB disk.<br>
If you have plugged a usb pen, eject and remove it and retry again.</h4></center></form</body></html>'
	exit 1
fi

if test -n "$huge_disk"; then
	fmsg1="<p>At least one of your disks is greater than 2.2TB, to use its full capacity
it will be partitioned using GPT partitioning."
fi

if blkid | grep -qE 'TYPE="ext(2|3|4)"'; then
	has_linuxfs=yes
fi

# FIXME: if a disk with no ext2/3/4 is plugged, should't the "no touch disk" checkbox be enabled?

if test -z "$has_linuxfs" -a -f /tmp/firstboot; then
	notouch_dis="disabled"
	std_chk="checked"
	cat<<-EOF
		<script type="text/javascript">
			alert("Your disks don't have linux filesystems," + '\n' +
			"and at least one must exists to continue," + '\n' +
			"disabling the \"Don't touch my disks\" option.")
		</script>
	EOF
else
	notouch_chk="checked"
fi

cat<<-EOF
	<fieldset>
	<legend>Whirl your magic wand...</legend>
	$fmsg
	<table>
	<tr><td colspan=2>I want my disk as:</td></tr>
	<tr><td align=center>
		<input type=radio $notouch_chk $notouch_dis name=wish_part value=notouch></td>
		<td>Don't touch my disks in any way!</td></tr>
	<tr><td align=center>
		<input type=radio $std_chk name=wish_part value=standard></td>
		<td>One big filesystem per disk, for easy management (standard)</td></tr>
	<tr><td align=center>
		<input type=radio name=wish_part value=jbd></td>
		<td>Merge all disks in one big filesystem, low data security (JBOD)</td></tr>
	<tr><td align=center>
		<input type=radio name=wish_part value=raid0></td>
		<td>Maximum performance and space with two or three disks (one an external USB disk), but low data security (raid0)</td></tr>
	<tr><td align=center>
		<input type=radio name=wish_part value=raid1></td>
		<td>Data security, duplicate everything on two disks (and use an external USB disk, if available, as a spare) (raid1)</td></tr>
	<tr><td align=center>
		<input type=radio name=wish_part value=raid5></td>
		<td>Data security and space, with two disks plus an external USB disk (raid5). Complex maintenance.</td></tr>

	<tr><td colspan=2><br>And I want the filesystems to be:<br></td></tr>
	<tr><td align=center>
		<input type=radio name=wish_fs value=ext2></td>
		<td>older, stable and faster (ext2)</td></tr>
	<tr><td align=center>
		<input type=radio name=wish_fs value=ext3></td>
		<td>fast cleaning time, improved reliability (ext3)</td></tr>
	<tr><td align=center>
		<input type=radio checked name=wish_fs value=ext4></td>
		<td>recent, faster cleaning time, best reliability, low fragmentation, big files support (ext4)</td></tr>
	</table></fieldset>

	<input type=submit name=advise value=Abracadabra onclick="return validate('$ndisks')">
	</form></body></html>
EOF

