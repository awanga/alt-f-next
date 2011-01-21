#!/bin/sh 

# check if any disk in an MD array is in standby
# blkid, used by plabel, wakes up a MD component disk if it has no filesys?
md_standby() {
	local mdev i
	mdev=$1
	for i in $(ls /sys/block/$mdev/slaves); do
		if test "$(disk_power ${i:0:3})" = "standby"; then return 0; fi
	done
	return 1
}

# $1=/dev/sda
disk() {
	dsk=$(basename $1)
	if test -b /dev/$dsk; then
		temp="--"; fam=""; mod="None"; tcap=""; pstatus="--"; health_st="--"
		disk_details $dsk

		cat<<-EOF
			<tr align=center>
			<td align=left>$dbay</td>
			<td>$dsk</td>
			<td align=left>$dmod</td>
			<td> $dcap </td>
			<td id=${dsk}_pstatus_id> $pstatus </td>
			<td id=${dsk}_temp_id> $temp </td> 
			<td id=${dsk}_health_id> $health_st </td>
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

		cnt=""; dirty=""; days=""
		if test "$type" == "ext2" -o "$type" == "ext3" -o "$type" == "ext4"; then
			res=$(tune2fs -l $dsk 2> /dev/null)
			if test $? = 0; then
				eval $(echo "$res" | awk \
					'/state:/ { if ($3 != "clean") printf "dirty=*;"} \
					/Mount/ {FS=":"; curr_cnt=$2} \
					/Maximum/ {FS=":"; max_cnt=$2} \
					/Next check after:/ {FS=" "; 
						mth = index("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", $5) / 4 + 1; 
						printf "days=\"%s-%d-%s %s\";", $8, mth, $6, $7 } 
					END {printf "cnt=%d;", max_cnt-curr_cnt}')
			fi

			if test -n "$days"; then
				days=$(expr \( $(date -d "$days" +%s) - $(date +%s) \) / 86400)
				if test "$days" -lt 5 ; then
					days="<font color=red> $days days</font>"
				else
					days="$days days"
				 fi
			fi

			if test -n "$cnt"; then
				if test "$cnt" -lt 5 ; then
					cnt="<font color=red> $cnt mounts or</font>"
				else
					cnt="$cnt mounts or"
				fi
			fi
		fi
	fi

	MD="$(awk '$1 == "/dev/'$dev'" { n = split($4, a,",")
		for (i=1;i<=n;i++)
			if (a[i] == "ro")
				printf ("<font color=red> %s </font>", toupper(a[i]))
			else if(a[i] == "rw")
				print toupper(a[i]) }' /proc/mounts)"

	cat<<-EOF
		<tr>
		<td>$dev</td>
		<td>$lbl</td>
		<td align=right>${cap}B</td>
		<td align=right>${free}B </td>
		<td>$type</td>
		<td>$MD</td>
		<td><font color=RED>$dirty</font> </td>
		<td>$cnt $days</td>
		</tr>
	EOF
}

. common.sh

arefresh="no"

if test -n "$QUERY_STRING"; then
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')
fi

# do this early, to avoid affecting the load value		
load=$(cut -f1 -d" " /proc/loadavg)

# smartctl is too slow, launch it in background, wait for them all at the script end
# launch a job for each disk, in parallel. As it is IO bound, CPU can be used meanwhyle
for i in /dev/sd?; do
	smartctl -n standby -iAH $i 2>&1 1> /tmp/smt_$(basename $i) &
done

if isflashed; then
	flash="Flashed"
fi
ver="$(cat /etc/Alt-F)"
write_header "$flash Alt-F $ver Status Page"

cat<<EOF
	<script type="text/javascript">
		function smart_fill(disk, health, temp, pstatus) {
			document.getElementById(disk + "_pstatus_id").innerHTML = pstatus
			document.getElementById(disk + "_temp_id").innerHTML = temp
			document.getElementById(disk + "_health_id").innerHTML = health
		}
	</script>
	<form name=statusf>
EOF

board="$(cat /tmp/board)"

if test $board != "C1"; then 
	temp_dev="/sys/class/hwmon/hwmon1/device/temp1_input"
	fan_dev="/sys/class/hwmon/hwmon0/device/fan1_input"
else
	temp_dev="/sys/class/hwmon/hwmon0/device/temp1_input"
	fan_dev="/sys/class/hwmon/hwmon1/device/fan1_input"
fi

eval $(cat $temp_dev | awk '{printf "temp=\"%.1f\"", $1 / 1000 }')
fan=$(cat $fan_dev)

if test $board != "C1"; then
	fan="$fan RPM"
else
	if test "$fan" -eq 0; then
		fan="Off"
	elif test "$fan" -le 400; then
		fan="Low"
	else
		fan="High"
	fi
fi

eval $(awk '{ days = $1/86400; hours = $1 % 86400 / 3600; \
	printf "up=\"%d day(s) %d hour(s)\"", days, hours }' /proc/uptime)

eval $(ethtool eth0 | awk '/Speed/{printf "Speed=%s", $2}')

eval $(ifconfig eth0 | awk \
		'/RX bytes/{printf "Rx=\"%s %s\";", $3, $4} \
		/TX bytes/{printf "Tx=\"%s %s\";", $7, $8} \
		/MTU/{printf "MTU=%s;", substr($0, match($a,"MTU")+4,5)} \
		/HWaddr/{printf "MAC=\"%s\";", $5}' | tr "()" "  ")

eval $(free | awk '/Swap/{printf "swap=\"%.1f/%d MB\"", $3/1024, $4/1024}')

cat <<-EOF
	<fieldset><Legend><strong> System </strong></legend><table>
	<tr>
		<td><strong>Temperature:</strong> $temp</td>
		<td><strong>Fan speed:</strong> $fan </td>
		<td><strong> Load:</strong> $load</td>
	</tr><tr>
		<td><strong>Swap:</strong> $swap</td>
		<td><strong>Uptime:</strong> $up</td>
		<td><strong>Date:</strong> $(date)</td>
	</tr></table>
	</fieldset><br>

	<fieldset><Legend><strong> Network </strong></legend>
	<strong> Speed: </strong> $Speed
	<strong> MTU: </strong> $MTU
	<strong> TX: </strong> $Tx
	<strong> Rx: </strong> $Rx
	<strong> MAC: </strong> $MAC
	</fieldset><br>
EOF

if has_disks; then
	cat<<-EOF
		<fieldset><Legend><strong> Disks </strong></legend><table>
		<tr align=center><td align=left><strong> Bay </strong></td>
		<th>Dev.</th>
		<th>Model</th>
		<th>Capacity</th>
		<th>Power Status</th>
		<th>Temp</th>
		<th>Health</th>
		</tr>
	EOF

	for i in /dev/sd?; do
		disk $i
	done

	echo "</table></fieldset><br>"
fi

if test -e /proc/mdstat -a -n "$(grep ^md /proc/mdstat 2> /dev/null)"; then
	cat<<-EOF
		<fieldset><Legend><strong> RAID </strong></legend><table>
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
		state=$(cat /sys/block/$mdev/md/array_state)
		type=$(cat /sys/block/$mdev/md/level)

		sz=""; deg=""; act=""; compl=""; exp="";
		if test "$state" != "inactive"; then
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
			<td align=left>$mdev</td> 
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
	echo "</table></fieldset><br>"
fi

if grep -q '^/dev/\(sd\|md\)' /proc/mounts; then
	cat<<-EOF
		<fieldset><legend><strong> Mounted Filesystems </strong></legend>
		<table>
		<tr align=center>
		<th>Dev.</th>
		<th>Label</th>
		<th>Capacity</th><th>Available</th>
		<th>FS</th><th>Mode</th>
		<th>Dirty</th><th>Automatic FSCK in</th> 
		</tr>
	EOF

	while read dev mnt fs rest; do
		dsk=$(echo $dev | grep '^/dev/\(sd\|md\)')
		if test -n "$dsk"; then
			filesys $dsk
		fi
	done < /proc/mounts

	echo "</table></fieldset><br>"
fi

if grep -q '\(nfs \|cifs\)' /proc/mounts; then
	cat<<-EOF
		<fieldset><Legend><strong>Mounted Remote Filesystems </strong></legend><table>
		<table>
		<tr align=center>
		<th>Host</th>
		<th>Remote Dir/Share</th>
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
				rrhost=${rhost%:*}
				rrdir=${rhost#*:/}
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
	echo "</table></fieldset><br>"
fi

if rcsmb status >& /dev/null; then
	smbm="$(smbstatus -S 2> /dev/null | tail -n +4)"
fi

if rcnfs status >& /dev/null; then
	nfsm="$(showmount --no-headers --all 2> /dev/null)"
fi

if test -n "$smbm" -o -n "$nfsm"; then
	cat<<-EOF
		<fieldset><Legend><strong>Remotely Mounted Filesystems </strong></legend><table>
		<table>
		<tr align=center>
		<th>Host</th>
		<th>Dir/Share</th>
		<th>FS</th>
		</tr>
	EOF

	if test -n "$smbm"; then
		echo "$smbm" | awk '{ 
				srv = NF - 7
				pos = index($0, $(srv + 1))
				share = substr($0, 1, pos-1)
				host = $(srv+2)
				printf "<tr><td>%s</td><td>%s</td><td>cifs</td></tr>\n", host, share
			}' | sort -u
	fi

	if test -n "$nfsm"; then
		IFS=:
		echo "$nfsm" | while read host dir; do
			if checkip "$host"; then
				if ! th=$(awk '/^'$host'/{print $3; exit 1}' /etc/hosts); then
					host=$th
				fi
			fi
			echo "<tr><td>$host</td><td>$dir</td><td>nfs</td></tr>"
		done
		IFS=" "
	fi
	echo "</table></fieldset><br>"
fi

pso=$(ps | grep "backup *[0-9]")
if test -n "$pso"; then

	if test -e /var/run/backup.pid; then
		bpid=$(cat /var/run/backup.pid)
		if kill -USR1 $bpid >& /dev/null; then
			active=$(echo "$pso" | grep $bpid | awk '{print $5}')
		fi
	fi

	cat<<-EOF
		<fieldset><Legend><strong> Backups </strong></legend>
		<table><tr><th>ID</th><th>Directory</th><th>State</th></tr>
	EOF

	for i in $(echo "$pso" | awk '{print $5}'); do
		if ! isnumber $i; then continue; fi
		bdir=$(grep ^$i /etc/backup.conf | cut -d";" -f4)
		st="Queued"
		if test "$i" = "$active"; then
			st="<font color=red>In progress</font>"
		fi
		echo "<tr><td>$i</td><td>$bdir</td><td align=center>$st</td></tr>"
	done
	echo "</table></fieldset><br>"
fi

if test -n "$(ls /tmp/clean-* /tmp/format-* /tmp/convert-* /tmp/shrink-* \
				/tmp/enlarg-* /tmp/wip-* 2> /dev/null)"; then
	cat<<-EOF
		<fieldset><Legend><strong> Filesystem Maintenance </strong></legend>
		<table><tr><th>Part.</th><th>Label</th><th>Operation</th></tr>
	EOF

	for j in /dev/sd[a-z][1-9] /dev/md[0-9]*; do
		part=$(basename $j)
		fs_progress $part # global ln
		if test -n "$ln"; then
			cat<<-EOF
				<tr><td>$part</td><td>$(plabel $part)</td>
				<td><font color=RED>$ln</font></td></tr>
			EOF
		fi
	done
	echo "</table></fieldset><br>"
fi

if test -f /etc/printcap -a -n "$(grep '^[^#]' /etc/printcap 2> /dev/null)"; then
	cat<<-EOF
		<fieldset><Legend><strong> Printers </strong></legend><table>
		<tr align=center><th>Name</th><th>Model</th><th>Jobs</th></tr>
	EOF

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
	echo "</table></fieldset><br>"
fi

# now collect smartctl jobs output 
j=1
for i in /dev/sd?; do
	dsk=$(basename $i)
	health_st="unknown"; temp="??"; pstatus="unknown"
	wait %$j
	eval $(awk -v st=$? '
		/^194/ { printf "temp=\"%d\";", $10}
		/not support SMART|Device is in/ {
			print "health_st=\"unknown\";"
			if (st == 2) print "pstatus=\"standby\";"}
		/SMART overall-health/ {
			if (st == 0) color="black"
			else if  (st == 32) color="blue"
			else color="red"
			printf "health_st=\"<font color=%s>%s</font>\";", color, tolower($NF) }
		/Power mode is:/ { printf "pstatus=\"%s\";", 
			tolower(substr($0, index($0,":")+2))} ' /tmp/smt_$dsk)
		cat<<-EOF
			<script type="text/javascript">
				smart_fill('$dsk', '$health_st', '$temp', '$pstatus')
			</script>
		EOF
	rm -f /tmp/smt_$dsk
	j=$((j+1))
done

if test "$arefresh" = "yes"; then
	refr_chk=checked
	cat<<-EOF
		<script type="text/javascript">
			var tmo_id = setTimeout('window.location.assign("http://" + location.hostname + \
				"/cgi-bin/status.cgi?arefresh=yes")', 15000)
		</script>
	EOF
fi

cat<<EOF
	Autorefresh <input type=checkbox $refr_chk name=refresh value="yes" onclick="frefresh(this)">
	<script type="text/javascript">
		var tmo_id
		function frefresh(obj) {
			arg = obj.checked == true ? "yes" : "no"
			obj.value = arg

			if (arg == "yes") {
				url = "http://" + location.hostname + "/cgi-bin/status.cgi?arefresh=yes"
				tmo_id = setTimeout('window.location.assign(url)', 15000)
			} else {
				clearTimeout(tmo_id)
			}
		}
	</script>
	</form></body></html>
EOF

