#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

dstatus() {
	local res dsk
	dsk=$1
	
	if test -b /dev/$dsk; then
		res=$(hdparm -C /dev/$dsk | awk '/drive/{print $4}') >/dev/null 2>&1
		#res="$(eval echo \$power_mode_$dsk)" # delayed results, not actual value
	else
		res="None"
	fi
	echo $res
}

. common.sh

check_cookie
write_header "Disc Utilities"

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
	<fieldset><Legend> $s Set mounted partitions to be checked every $es </legend>
	<input type=text size=4 name=mounts value=$mounts> mounts
	or every <input type=text size=4 name=days value=$days> days
	<input type=submit name=tune value=Submit>
	</fieldset><br>

	<fieldset><Legend> $s Utilities $es </legend>
	<TABLE>
	<TR align=center><TD> $s Bay $es </td>
	<TD> $s Disk Model $es </td>
	<td></td>
	<td> $s Health $es </td>
	<td> $s P. Mode $es </td>
	<td></td>
	<td columnspan=2> $s Set Standby $es</td> 
EOF

#for i in right left usb; do
while read ln; do
  if test -z "$ln"; then continue; fi
  eval $(echo $ln | awk '{printf "bay=%s;dsk=%s", $1, $2}')
  stat=$(dstatus $dsk)
	mod=$(cat /sys/block/$dsk/device/model)
  eval "val=\$$bay"
 
  cat<<-EOF
	<TR>
        <TD> $s $bay $es </TD>
	<td> $mod </td>
EOF

  if ! test -b "/dev/$dsk"; then
    echo "<td></td><td></td><td></td><td></td>"
  else
   cat<<-EOF	 
        <TD> <input type="submit" name="$dsk" value="Eject"> </TD>
	<TD> <input type="submit" name="$dsk" value="Check"> </TD>
        <TD> $stat </TD>
        <TD> <input type="submit" name="$dsk" value="StandbyNow"> </TD>
EOF
  fi

  echo "<TD><input type="text" SIZE=4 name="$bay" value="$val"> minutes</TD></TR>"

done < /etc/bay

cat<<-EOF
	<tr>
        <TD></TD> <TD></TD> <TD></TD><TD></TD><TD></TD><TD></TD>
	<TD><input type="submit" name="standby" value="Submit"> </TD>
	</TR>        
	</TABLE>
	</fieldset>
	</form>
</body></html>
EOF
