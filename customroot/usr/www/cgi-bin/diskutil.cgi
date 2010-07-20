#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

dstatus() {
	local res dsk
	dsk=$1
	
	if test -b /dev/$dsk; then
		res=$(hdparm -C /dev/$dsk | awk '/drive/{print $4}') >/dev/null 2>&1
	else
		res="None"
	fi
	echo $res
}

. common.sh

check_cookie
write_header "Disk Utilities"

s="<strong>"
es="</strong>"
c="<center>"
ec="</center>"

disks=$(ls /dev/sd?) >/dev/null 2>&1

if test -z "$disks"; then
        echo "<br> $s No disks found! $es <br>"
        echo "</body></html>"
        exit 1
fi

CONFF=/etc/hdsleep.conf
CONFT=/etc/tune.conf

. /tmp/power_mode

if test -f $CONFF; then
	while read  line; do
		eval $(echo $line | awk '!/#/{if (NF == 2) print $1 "=" $2}')
	done < $CONFF
else
	right=90
	left=90
	usb=90	
	echo -e "right $right\nleft $left\nusb $usb"
fi

if test -f $CONFT; then
	while read  line; do
		eval $(echo $line | awk '!/#/{if (NF == 2) print $1 "=" $2}')
	done < $CONFT
else
	mounts=50
	days=180
	echo -e "mounts $mounts\ndays $days"
fi

cat<<EOF
	<form action="/cgi-bin/diskutil_proc.cgi" method="post">
	<fieldset><Legend> $s Disks $es </legend>
	<table>
	<tr align=center><th>Bay</th>
	<th>Dev.</th>
	<th>Disk Model</th>
	<th></th>
	<th>Health</th>
	<th>P. Mode</th>
	<th></th>
	<th columnspan=2>Set Standby</th> 
EOF

while read ln; do
	if test -z "$ln"; then continue; fi
	eval $(echo $ln | awk '{printf "bay=%s;dsk=%s", $1, $2}')
	stat=$(dstatus $dsk)
	poweren=""
	if test "$stat" = "unknown"; then poweren="disabled"; fi
	mod=$(cat /sys/block/$dsk/device/model)
	eval "val=\$$bay"
 
	echo "<tr><td> $s $bay $es </td><td>$dsk</td><td> $mod </td>"

	if ! test -b "/dev/$dsk"; then
		echo "<td></td><td></td><td></td><td></td>"
	else
		if eject -s $dsk > /dev/null; then
			ejectop="Load"
		else
			ejectop="Eject"
		fi
		cat<<-EOF	 
			<td> <input type="submit" name="$dsk" value="$ejectop"> </td>
			<td> <input type="submit" name="$dsk" value="Status"> </td>
			<td> $stat </td>
			<td> <input type="submit" $poweren name="$dsk" value="StandbyNow"> </td>
		EOF
	fi

	echo "<td><input type="text" size=4 name="$bay" value="$val"> minutes</td></tr>"
done < /etc/bay

cat<<-EOF
	<tr>
	<td colspan=7></td>
	<td><input type="submit" name="standby" value="Submit"> </td>
	</tr>        
	</table>
	</fieldset><br>

	<fieldset><Legend> $s Set mounted partitions to be checked every $es </legend>
	<input type=text size=4 name=mounts value=$mounts> mounts
	or every <input type=text size=4 name=days value=$days> days
	<input type=submit name=tune value=Submit>
	</fieldset><br>
	</form></body></html>
EOF
