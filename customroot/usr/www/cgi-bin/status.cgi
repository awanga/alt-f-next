#!/bin/sh 

# check if any disk in an MD array is in standby
# blkid, used by plabel, wakes up a MD component disk if it has no filesys?
md_standby() {
	local mdev i
	mdev=$1
	for i in $(ls /sys/block/$mdev/slaves); do
		if test "$(eval echo \$power_mode_${i:0:3})" = "standby"; then
			#eval check_${i:5:7}="NO"
			return 0
		fi
	done
	return 1
}

disk() {
	nm="$1"
	dsk="$2"
	temp="??"
	fam=""
	mod="None"
	tcap=""
	pstatus=""
	health_st=""

	if test -b /dev/$dsk; then
		mod=$(cat /sys/block/$dsk/device/model)
		tcap=$(awk -v sz=$(cat /sys/block/$dsk/size) 'BEGIN{printf "%.1fG", sz*512/1e9}' /dev/null)
		pstatus="$(eval echo \$power_mode_$dsk)"
		if test "$pstatus" != "standby"; then
			# smartctl is too slow, +/- 0.5 sec
			res=$(smartctl -iA /dev/$dsk)
			if test $? = "0"; then
				health_st="OK"
			elif test $? = "1"; then
				health_st="unknown"
			else
				health_st="<font color=red> Failing</font>"
			fi
			eval $(echo "$res" | awk '/^194/ {printf "temp=\"%d\";", $10}
				/^Model Family/ {printf "fam=\"%s\";", $3}
				/^Device:/ {printf "fam=\"%s\";", $2}')
		fi
	fi	

	echo "<tr align=center>
			<td align=left> $s $nm $es </td>
			<td align=left> $fam $mod</td>
			<td> $tcap </td>
			<td> $pstatus </td>
			<td> $temp </td> 
			<td> $health_st </td>
			</tr>"
}

filesys() {
	dsk="$1"
	type=$2
	lbl="$(plabel $dsk)"
	if test -z "$lbl"; then lbl=$dsk; fi
	
	if test -b /dev/$dsk; then
		cnt=""; dirty="";
		eval $(df -h /dev/$dsk | awk '/'$dsk'/{printf "cap=%s;free=%s", $2, $4}')
		res=$(tune2fs -l /dev/$dsk 2> /dev/null)
		if test $? = 0; then
			eval $(echo "$res" | awk \
				'/state:/{ if ($3 != "clean") printf "dirty=*;"} \
				/Mount/{FS=":"; curr_cnt=$2} \
				/Maximum/{FS=":"; max_cnt=$2} \
				END{printf "cnt=%d", max_cnt-curr_cnt}')
		fi
	fi

	if test "$cnt" -lt 5; then cnt="<font color=RED> $cnt </font>"; fi
	echo "<tr align=center>
		<td align=left>$lbl </td>
		<td> $cap </td> <td>$free </td>
		<td> $type </td>
		<td> <font color=RED> $dirty </font> </td>
		<td> $cnt </td>
		</tr>"
}

main() {

. common.sh
#check_cookie # status don't need passwd
ver=$(cat /etc/Alt-F)
write_header "Alt-F $ver Status Page" 15

fan_dev="/sys/class/hwmon/hwmon0/device/fan1_input"
temp_dev="/sys/class/hwmon/hwmon1/device/temp1_input"

p="<p>"
ep="</p>"
s="<strong>"
es="</strong>"

# do this early, to avoid affecting the load value		
eval $(uptime | awk '{i=3; msg=""; while ($i != "load") \
	{ msg=msg " " $i; i++; } printf "out=\"%s\"; load=%s", msg, $(i+2)}')

eval $(ethtool eth0 | awk '/Speed/{printf "Speed=%s", $2}')

eval $(ifconfig eth0 | awk \
		'/RX bytes/{printf "Rx=\"%s %s\";", $3, $4} \
		/TX bytes/{printf "Tx=\"%s %s\";", $7, $8} \
		/MTU/{printf "MTU=%s;", substr($5, 5)} \
		/HWaddr/{printf "MAC=\"%s\";", $5}' | tr "()" "  ")

eval $(cat $temp_dev | awk '{printf "temp=\"%.1f\"", $1 / 1000 }')

eval $(free | awk '/Swap/{printf "swap=\"%d/%d MB\"", $3/1024, $4/1024}')

cat <<-EOF
	<fieldset><Legend> $s System $es </legend>
	$s Temperature:	 $es  $temp C
	$s Fan speed:  $es $(cat $fan_dev) RPM 
	<br> $s Uptime:	 $es $out $s Load: $es $load  
	$s Swap:  $es $swap 
	</fieldset><br>

	<fieldset><Legend> $s Network $es </legend>
	$s Speed: $es $Speed
	$s MTU: $es $MTU
	$s TX: $es $Tx
	$s Rx: $es $Rx
	$s MAC: $es $MAC
	</fieldset><br>

	<fieldset><Legend> $s Disks $es </legend><table>
EOF

. /tmp/power_mode

if test -z "$(ls /dev/sd?? 2>/dev/null)"; then
	echo "None<br>"
else
	cat<<-EOF
		<tr align=center><td align=left> $s Bay $es </td>
		<td> $s Model $es </td>
		<td> $s Capacity $es </td>
		<td> $s Power Status $es </td>
		<td> $s Temp $es C </td>
		<td> $s Health $es </td>
		</tr>
	EOF

	disk Right $(awk '/right/{print $2}' /etc/bay)
	disk Left $(awk '/left/{print $2}' /etc/bay)

	while read ln; do
		dsk=$(echo $ln | awk '/usb/{print $2}') 
		if test -n "$dsk"; then
			disk USB $dsk
		fi
	done < /etc/bay
fi

cat<<-EOF
	</table></fieldset><br>
	<fieldset><legend> $s Mounted Filesystems $es </legend>
EOF

if test -z "$(awk '/^\/dev\/(sd|md)/{ print "yes"}' /proc/mounts)"; then
	echo "None"
else
	cat<<-EOF
		<table>
		<tr align=center>
		<td align=left> $s Label $es </td>
		<td> $s Capacity $es</td> <td> $s Available $es</td>
		<td> $s FS $es </td><td> $s Dirty $es </td> <td> $s FSCK $es </td> 
		</tr>
	EOF

	while read dev mnt type rest; do
		dsk=$(echo $dev | grep '^/dev/\(sd\|md\)')
		if test -n "$dsk"; then
			filesys $(basename $dsk) $type
		fi
	done < /proc/mounts
fi

cat<<-EOF
	</table></fieldset><br>
	<fieldset><Legend> $s RAID $es </legend><table>
EOF

#echo $check_md0, $check_md1, $check_md2

if ! test -e /proc/mdstat; then
	echo "None<br>"
elif test -z "$(grep ^md /proc/mdstat)"; then
	echo "None<br>"
else
	echo "<tr align=center>
		<td align=left> $s Label $es </td> 
		<td> $s Capacity $es</td>
		<td> $s Type $es </td> <td> $s State $es </td>
		<td> $s Status $es </td> <td> $s Action $es </td>
		<td> $s Done $es </td> <td> $s ETA $es </td>
 		</tr>"

	for i in /dev/md[0-9]*; do
		mdev=$(basename $i)
		if $(md_standby $mdev); then
			lbl=$mdev
		else
			lbl=$(plabel $mdev)
			if test -z "$lbl"; then lbl=$mdev; fi
		fi
		state=$(cat /sys/block/$mdev/md/array_state)
		type=$(cat /sys/block/$mdev/md/level)

		if test $? = 1; then lbl=$mdev; fi
		sz=""; deg=""; act=""; compl=""; exp="";
		if test "$state" != "inactive"; then
			eval $(df -h | awk '/'$mdev'/{printf "sz=%s", $2}')
			if test "$type" = "raid1" -o "$type" = "raid5"; then
				if test "$(cat /sys/block/$mdev/md/degraded)" != 0; then
					deg="<font color=RED> degraded </font>"
				else
					deg="OK"
				fi
				act=$(cat /sys/block/$mdev/md/sync_action)
				if test "$act" != "idle"; then
					compl=$(awk '{printf "%.1f%%", $1 * 100 / $3}' /sys/block/$mdev/md/sync_completed)
					speed=$(cat /sys/block/$mdev/md/sync_speed)
					exp=$(awk '{printf "%.1fmin", ($3 - $1) * 512 / 1000 / '$speed' / 60 }' /sys/block/$mdev/md/sync_completed)
				fi
			fi
		fi
		echo "<tr align=center>
			<td align=left>$lbl</td> 
			<td>$sz</td>
			<td>$type</td> <td>$state</td>
			<td>$deg</td> <td>$act</td> <td>$compl</td> <td>$exp</td>
			</tr>"
	done
fi

cat <<-EOF
	</table></fieldset><br>
	<fieldset><Legend> $s Printers $es </legend><table>
EOF

if ! test -f /etc/printcap; then
	echo "None"
else
	echo "<tr align=center><td> $s Name $es</td>
		<td> $s Model $es </td><td> $s Jobs $es</td></tr>"

	while read ln; do
		if test "${ln:0:1}" = "#"; then continue; fi
		jb="?"
		eval $(echo $ln | sed 's/:/|/g' | \
			awk -F '|' '{printf "pr=%s;desc=\"%s\";%s", $1, $2, $3}')
		if test -d /var/spool/lpd/$pr; then
			#host="local"
			jb=$(ls /var/spool/lpd/$pr | wc -l)
		else
			#host="remote"
			if test -f /usr/bin/lpstat; then
				jb=$(lpstat | grep ^$pr | wc -l)
			fi
		fi
		echo "<tr><td>$pr</td><td>$desc</td><td>$jb</td></tr>"
		
	done < /etc/printcap
fi
echo "</table></fieldset><br>"

#cat <<-EOF
#	<fieldset><Legend> $s Software versions $es </legend>
#	$s Alt-F: $es $(awk '/version/{print $2}' /etc/Alt-F)
#	$s Linux: $es $(uname -r) 
#	$s BusyBox: $es $(awk '/version:/ {print $4}' /boot/busybox.config) 
#	$s Uclib: $es $(awk '/Version:/ {print $3}' /boot/uclibc.config) 
#	</fieldset>
#EOF

echo "</body></html>"

}

# generating the status page is a slow process, the page being draw in
# the browser as it is generated, which looks bad.
# to avoid this, the page is generated to a temporary file and sent when
# all is done. 
# The time spent is the same, but not seeing the page being slowly
# generated
# avoids the slowness sensation

TF=/tmp/.status.tmp

main > $TF 2>&1
cat $TF
rm $TF >/dev/null 2>&1
