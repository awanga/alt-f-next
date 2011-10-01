#!/bin/sh

. common.sh
check_cookie
write_header "Disk Wizard"

if test -f /tmp/firstboot; then
	cat<<-EOF
		<center>
		<h3>Welcome to your first login to Alt-F</h3>
		<h4>To continue setting up Alt-F, you should now choose a disk configuration.</h4>
		</center>
	EOF
fi

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
	<fieldset>
	<legend><strong>Detected disks</strong></legend>
	<table><tr>
	<th>Bay</th>
	<th>Device</th>
	<th>Capacity</th>
	<th>Model</th>
	</tr>
EOF

for i in $disks; do
	disk=$(basename $i)

	disk_details $disk

	if test "$(cat /sys/block/${disk}/size)" -gt 3907024065; then
		huge_disk="yes"
	fi

	chkd=""	
	if test "$i" = "$dsk"; then chkd="checked"; fi

	cat<<-EOF
		<tr>
		<td>$dbay</td>
		<td align=center>$disk</td>
		<td align=right>$dcap</td>
		<td>$dmod</td>
		</tr>
	EOF
done
echo "</table></fieldset><br>"	

nusb="$(cat /etc/bay | grep =usb | wc -l)"
if test  "$nusb" -ge 2; then
	echo "<center><h4>For performance reasons you should have no more than one external USB disk.<br>
If you have plugged a usb pen, eject and remove it and retry again.</h4></center></form</body></html>"
	exit 1
fi

if test -n "$huge_disk"; then
	fmsg1="<p>At least one of your disks is greater than 2.2TB, to use its full capacity
it will be partitioned using GPT partitioning."
fi

if isflashed; then
	std_chk="checked"
	ext4_chk="checked"
else
	notouch_chk="checked"
	ext3_chk="checked"
	ext4_dis="disabled"
	raid5_dis="disabled"
	cat<<-EOF
		<script type="text/javascript">
			alert("Your box is not Alt-F flashed, some options not recognized by the stock firmware," + '\n' +
			"such as the ext4 filesystem, RAID-5 and GPT partitioning, are not available," + '\n' +
			"as the stock firmware would not recognize them.")
		</script>
	EOF
fi

cat<<-EOF
	<form name=wizf action="/cgi-bin/diskwiz_proc.cgi" method="post">
	<fieldset>
	<legend><strong>Whirl your magic wand...</strong></legend>
	$fmsg
	<table>
	<tr><td colspan=2>I want my disk as:</td></tr>
	<tr><td align=center>
		<input type=radio $notouch_chk name=wish_part value=notouch></td>
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
		<input type=radio $raid5_dis name=wish_part value=raid5></td>
		<td>Data security and space, with two disks plus an external USB disk (raid5)</td></tr>

	<tr><td colspan=2><br>And I want the filesystems to be:<br></td></tr>
	<tr><td align=center>
		<input type=radio name=wish_fs value=ext2></td>
		<td>older, stable and faster (ext2)</td></tr>
	<tr><td align=center>
		<input type=radio $ext3_chk name=wish_fs value=ext3></td>
		<td>fast cleaning time, improved reliability (ext3)</td></tr>
	<tr><td align=center>
		<input type=radio $ext4_dis $ext4_chk name=wish_fs value=ext4></td>
		<td>recent, faster cleaning time, best reliability, low fragmentation, big files support (ext4)</td></tr>

	<tr><td align=center>
		<input type=submit name=advise value=Abracadabra onclick="return validate('$ndisks')"></td></tr>

	</table></fieldset>
	</form></body></html>
EOF

