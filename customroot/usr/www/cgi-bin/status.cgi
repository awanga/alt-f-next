#!/bin/sh 

# check if any disk in an MD array is in standby
# blkid, used by plabel, wakes up a MD component disk if it has no filesys?
md_standby() {
	local mdev i
	mdev=$1
	for i in $(ls /sys/block/$mdev/slaves); do
		if test "$(eval echo \$power_mode_${i:0:3})" = "standby"; then
			return 0
		fi
	done
	return 1
}

# $1-device
smart() {
	health_st=""; temp="??"; fam=""; pstatus="unknown"
	res=$(smartctl -n standby -iAH /dev/$1)
	st=$?
	eval $(echo "$res" | awk -v st=$st '
		/^194/ {printf "temp=\"%d\";", $10}
		/^Model Family/ {printf "fam=\"%s\";", $3}
		/^Device:/ {printf "fam=\"%s\";", $2}
		/not support SMART|Device is in/ { print "health_st=\"unknown\";"
			if (st == 2) print "pstatus=\"standby\";"}
		/SMART overall-health/ {
			if (st == 0) color="black"
			else if  (st == 32) color="blue"
			else color="red"
			printf "health_st=\"<font color=%s>%s</font>\";", color, tolower($NF) }
		/Power mode is:/ { printf "pstatus=\"%s\";", 
			tolower(substr($0, index($0,":")+2))}')
	echo "health_st=\"$health_st\"; temp=$temp; fam=\"$fam\"; pstatus=\"$pstatus\"" > /tmp/SMART-$1
}

disk() {
	nm="$1"
	dsk="$2"
	temp="--"; fam=""; mod="None"; tcap=""; pstatus="--"; health_st="--"

	if test -b /dev/$dsk; then
		mod=$(cat /sys/block/$dsk/device/model)
		tcap=$(awk '{printf "%.1f GB", $1*0.5e-6}' /sys/block/$dsk/size)
		# smartctl is too slow, +/- 0.5 sec, use the *previous* value if not older than 2 minutes
		if ! test -f /tmp/SMART-$dsk; then
			smart $dsk
		elif test "$(expr $(date +%s) - $(stat -t /tmp/SMART-$dsk | cut -d" " -f 14))" -lt 120; then
			. /tmp/SMART-$dsk
		else
			smart $dsk
		fi

		cat<<-EOF
			<tr align=center>
			<td align=left> $nm </td>
			<td>$dsk</td>
			<td align=left> $fam $mod</td>
			<td> $tcap </td>
			<td> $pstatus </td>
			<td> $temp </td> 
			<td> $health_st </td>
			</tr>
		EOF
	fi
}

filesys() {
	dsk="$1"
	dev=$(basename $dsk)
	
	if test -b $dsk; then
		eval $(df -h $dsk | awk '/'$dev'/{printf "cap=%s;free=%s", $2, $4}')
		type=$(blkid -s TYPE -o value $dsk)
		lbl="$(plabel $dsk)"

		cnt=""; dirty="";
		res=$(tune2fs -l $dsk 2> /dev/null)
		if test $? = 0; then
			eval $(echo "$res" | awk \
				'/state:/{ if ($3 != "clean") printf "dirty=*;"} \
				/Mount/{FS=":"; curr_cnt=$2} \
				/Maximum/{FS=":"; max_cnt=$2} \
				END{printf "cnt=%d", max_cnt-curr_cnt}')
		fi
		MD="$(awk '$1 == "/dev/'$dev'" { n = split($4, a,",")
			for (i=1;i<=n;i++)
				if (a[i] == "ro")
					printf ("<font color=red> %s </font>", toupper(a[i]))
				else if(a[i] == "rw")
					print toupper(a[i]) }' /proc/mounts)"
	fi

	if test "$cnt" -lt 5; then cnt="<font color=red> $cnt </font>"; fi
	cat<<-EOF
		<tr>
		<td>$dev</td>
		<td>$lbl</td>
		<td align=right>${cap}B</td>
		<td align=right>${free}B </td>
		<td>$type</td>
		<td>$MD</td>
		<td><font color=RED>$dirty</font> </td>
		<td>$cnt</td>
		</tr>
	EOF
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
eval $(awk '{ days = $1/86400; hours = $1 % 86400 / 3600; \
	printf "up=\"%d day(s) %d hour(s)\"", days, hours }' /proc/uptime)

load=$(cut -f1 -d" " /proc/loadavg)

eval $(ethtool eth0 | awk '/Speed/{printf "Speed=%s", $2}')

eval $(ifconfig eth0 | awk \
		'/RX bytes/{printf "Rx=\"%s %s\";", $3, $4} \
		/TX bytes/{printf "Tx=\"%s %s\";", $7, $8} \
		/MTU/{printf "MTU=%s;", substr($0, match($a,"MTU")+4,5)} \
		/HWaddr/{printf "MAC=\"%s\";", $5}' | tr "()" "  ")

eval $(cat $temp_dev | awk '{printf "temp=\"%.1f\"", $1 / 1000 }')

eval $(free | awk '/Swap/{printf "swap=\"%.1f/%d MB\"", $3/1024, $4/1024}')

cat <<-EOF
	<fieldset><Legend> <strong> System </strong> </legend><table>
	<tr>
		<td><strong>Temperature:</strong>  $temp</td>
		<td><strong>Fan speed:</strong> $(cat $fan_dev) RPM</td>
		<td><strong> Load:</strong> $load</td>
	</tr><tr>
		<td><strong>Swap:</strong> $swap</td>
		<td><strong>Uptime:</strong> $up</td>
		<td><strong>Date:</strong> $(date)</td>
	</tr></table>
	</fieldset><br>

	<fieldset><Legend> <strong> Network </strong> </legend>
	<strong> Speed: </strong> $Speed
	<strong> MTU: </strong> $MTU
	<strong> TX: </strong> $Tx
	<strong> Rx: </strong> $Rx
	<strong> MAC: </strong> $MAC
	</fieldset><br>

	<fieldset><Legend> <strong> Disks </strong> </legend><table>
EOF

. /tmp/power_mode

if test -z "$(ls /dev/sd?? 2>/dev/null)"; then
	echo "None<br>"
else
	cat<<-EOF
		<tr align=center><td align=left> <strong> Bay </strong> </td>
		<th>Dev.</th>
		<th>Model</th>
		<th>Capacity</th>
		<th>Power Status</th>
		<th>Temp</th>
		<th>Health</th>
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
	<fieldset><legend> <strong> Mounted Filesystems </strong> </legend>
EOF

if ! grep -q '^/dev/\(sd\|md\)' /proc/mounts; then
	echo "None"
else
	cat<<-EOF
		<table>
		<tr align=center>
		<th>Dev.</th>
		<th>Label</th>
		<th>Capacity</th><th>Available</th>
		<th>FS</th><th>Mode</th>
		<th>Dirty</th><th>FSCK</th> 
		</tr>
	EOF

	while read dev mnt fs rest; do
		dsk=$(echo $dev | grep '^/dev/\(sd\|md\)')
		if test -n "$dsk"; then
			filesys $dsk
		fi
	done < /proc/mounts
fi

cat<<-EOF
	</table></fieldset><br>
	<fieldset><Legend> <strong>Mounted Remote Filesystems </strong> </legend><table>
EOF


if ! grep -q '\(nfs \|cifs\)' /proc/mounts; then
	echo "None"
else
	cat<<-EOF
		<table>
		<tr align=center>
		<th>Host</th>
		<th>Remote Dir</th>
		<th>Local Dir</th>
		<th>Capacity</th><th>Available</th>
		<th>FS</th>
		</tr>
	EOF

	while read rhost mnt fs rest; do
		if test "$fs" = "nfs" -o $fs = "cifs"; then
			if test "$fs" = "cifs"; then
				rrhost=$(echo $rhost | cut -d'/' -f3)
				rrdir=$(echo $rhost | cut -d'/' -f4)
			else 
				rrhost=${rhost%.*}
				rrdir=${rhost#*:}
			fi
			# "df" breaks lines when are long nfs host:dir 
			eval $(df -h "$mnt" | awk '{if (NF == 6) printf "sz=%sB; avai=%sB;", $2, $4
				if (NF == 5) printf "sz=%sB; avai=%sB;", $1, $3}')
			echo "<tr><td>$rrhost</td>
				<td>$rrdir</td><td>$mnt</td>
				<td>$sz</td><td>$avai</td>
				<td>$fs</td></tr>"
		fi
	done < /proc/mounts
fi

cat<<-EOF
	</table></fieldset><br>
	<fieldset><Legend> <strong> RAID </strong> </legend><table>
EOF

if ! test -e /proc/mdstat; then
	echo "None<br>"
elif test -z "$(grep ^md /proc/mdstat)"; then
	echo "None<br>"
else
	cat<<-EOF
		<tr align=center>
		<th align=left>Dev.</th> 
		<th>Capacity</th>
		<th>Level</th><th>State</th>
		<th>Status</th><th>Action</th>
		<th>Done</th><th>ETA</th>
 		</tr>
	EOF

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
			#eval $(df -h | awk '/'$mdev'/{printf "sz=%s", $2}')
			sz=$(awk '{ printf "%.1f GB", $1/2/1024/1024}' /sys/block/$mdev/size)
			if test "$type" = "raid1" -o "$type" = "raid5"; then
				if test "$(cat /sys/block/$mdev/md/degraded)" != 0; then
					deg="<font color=RED> degraded </font>"
				else
					deg="OK"
				fi
				act=$(cat /sys/block/$mdev/md/sync_action)
				if test "$act" != "idle"; then
					act="<font color=RED> $act </font>"
					compl=$(awk '{printf "%.1f%%", $1 * 100 / $3}' /sys/block/$mdev/md/sync_completed)
					speed=$(cat /sys/block/$mdev/md/sync_speed)
					exp=$(awk '{printf "%.1fmin", ($3 - $1) * 512 / 1000 / '$speed' / 60}' /sys/block/$mdev/md/sync_completed 2> /dev/null)
				fi
			fi
		fi
		cat<<-EOF
			<tr align=center>
			<td align=left>$lbl</td> 
			<td>$sz</td>
			<td>$type</td>
			<td>$state</td>
			<td>$deg</td>
			<td>$act</td>
			<td>$compl</td>
			<td>$exp</td>
			</tr>
		EOF
	done
fi

echo "</table></fieldset><br>"

fswork=""
for k in clean format convert shrink enlarg wip; do
	if ls /tmp/$k-* >& /dev/null; then
		fswork="true"
	fi
done

if test "$fswork" = "true"; then
	cat<<-EOF
		<fieldset><Legend> <strong> Filesystem Maintenance </strong> </legend>
		<table><tr><th>Part.</th><th>Label</th><th>Operation</th></tr>
	EOF

	for j in /dev/sd[a-z][1-9] /dev/md[0-9]*; do
		part=$(basename $j)
		for k in clean format convert shrink enlarg wip; do
			if test -f /tmp/$k-$part; then
				#if test -d /proc/$(cat /tmp/$k-$part.pid); then
				if kill -1 $(cat /tmp/$k-$part.pid) 2> /dev/null; then
					cat<<-EOF
						<tr><td>$part</td><td>$(plabel $part)</td>
						<td><font color=RED>${k}ing...</font></td>
						</tr>
					EOF
				else
					rm -f /tmp/$k-$part*
				fi
			fi
		done
	done
	echo "</table></fieldset>"
fi

echo "<fieldset><Legend> <strong> Printers </strong> </legend><table>"

if ! test -f /etc/printcap; then
	echo "None"
elif ! grep -q '^[^#]' /etc/printcap; then
	echo "None"
else
	echo "<tr align=center><th>Name</th><th>Model</th><th>Jobs</th></tr>"

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
				jb=$(lpstat 2> /dev/null | grep ^$pr | wc -l)
			fi
		fi
		echo "<tr><td>$pr</td><td>$desc</td><td>$jb</td></tr>"
		
	done < /etc/printcap
fi

cat<<-EOF
	</table></fieldset><br>
	</body></html>
EOF

}

# generating the status page is a slow process, the page being draw in
# the browser as it is generated, which looks bad.
# to avoid this, the page is generated to a temporary file and sent when
# all is done. 
# The time spent is the same, but not seeing the page being slowly
# generated avoids the slowness sensation
# hmmm, dont like it either.

if false; then
	TF=/tmp/.status.tmp

	main > $TF 2>&1
	cat $TF
	rm $TF >/dev/null 2>&1
else
	main
fi

# smartctl is too slow.
# Run it now and use the colected values in the *next* run
for i in /dev/sd?; do
	smart $(basename $i)
done
