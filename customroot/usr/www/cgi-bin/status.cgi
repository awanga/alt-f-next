#!/bin/sh 

. common.sh

# Based on original ideia and code contributed by Dwight Hubbard, dwight.hubbard <guess> gmail.com
# Modified and adapted by Joao Cardoso
launch() {
	echo "<div style=\"margin-bottom: 1.5em;\" id=\"$1\">"
	eval ${1}_st
	echo "</div>"
	return 0;
}

# Based on original ideia and code contributed by Dwight Hubbard, dwight.hubbard <guess> gmail.com
# Modified and adapted by Joao Cardoso
jscripts() {
	cat<<-EOF
		<script type="text/javascript">
			arefresh = false
			function requestfromserver(target, refresh) {
				var req = new XMLHttpRequest();    			
				if (req == null)
					return;

				req.onreadystatechange = function() {
					if (req.readyState != 4) return; // only if req is "loaded"
					if (req.status != 200) return; // only if "OK"
						document.getElementById(target).innerHTML = req.responseText;
					delete req;
					if (arefresh == true && refresh != 0)
						setTimeout(	function() {requestfromserver(target, refresh);}, refresh * 1000);
				}
				url="/cgi-bin/status.cgi?refresh=" + target
				req.open("GET", url, true);
				req.send();
			}

			function frefresh(obj) {
				arg = obj.checked == true ? "yes" : "no"
	
				if (arg == "yes") {
					arefresh = true
					requestfromserver('systems', 11)
					requestfromserver('network', 11)
					requestfromserver('disks', 13)
					requestfromserver('raid', 13)
					requestfromserver('mounted_filesystems', 17)
					requestfromserver('mounted_remote_filesystems', 17)
					requestfromserver('remotely_mounted_filesystems', 19)
					requestfromserver('backup', 19)
					requestfromserver('filesystem_maintenance', 23)
					requestfromserver('printers', 23)
				}
				else
					arefresh = false
			}
		</script>
	EOF
}

systems_st() {
	cpu="$(top -bn1 | awk '/^CPU:/ {printf "%d", 100 - $8}')"
	loadv=$(cut -f1 -d" " /proc/loadavg)
	load=$(awk '{printf "%d", 50 * $1 }' /proc/loadavg)

	eval $(free | awk '/Swap/{if ($2 == 0) printf "swap=0; swapv=None"; \
			else { printf "swap=%d; swapv=\"%.1f/%dMB\"", $3*100/$2, $3/1024, $4/1024}}')

	eval $(awk '{ days = $1/86400; hours = $1 % 86400 / 3600; \
		printf "up=\"%d day(s) %d hour(s)\"", days, hours }' /proc/uptime)

	board="$(cat /tmp/board)"

	if test "$board" = "Unknown"; then
		fan=0; 	fanv="Unknown"
		temp=0; tempv="Unknown"
	else
		if test "$board" = "A1" -o "$board" = "B1"; then 
			temp_dev="/sys/class/hwmon/hwmon1/device/temp1_input"
			fan_dev="/sys/class/hwmon/hwmon0/device/fan1_input"
		elif test "$board" = "C1" -o "$board" = "D1"; then
			temp_dev="/sys/class/hwmon/hwmon0/device/temp1_input"
			fan_dev="/sys/class/hwmon/hwmon1/device/fan1_input"
		fi

		if test "$board" = "A1" -o "$board" = "B1" -o "$board" = "C1"; then
			device="DNS-323 rev-$board"
		elif test "$board" = "D1"; then
			device="DNS-321 rev-A1"
		fi

		if test -f /etc/sysctrl.conf; then
			. /etc/sysctrl.conf
		else
			max_fan_speed=5500
			crit_temp=54
		fi

		eval $(awk '{printf "tempt=\"%.1f\"; temp=\"%d\"", $1 / 1000, $1 / 10 / '$crit_temp'}' $temp_dev)
		tempv="${tempt}&deg;C/$(celtofar $tempt)&deg;F"
		fan=$(cat $fan_dev)

		if test "$board" = "A1" -o "$board" = "B1"; then
			fanv=$fan
			fan=$(expr $fanv \* 100 / $max_fan_speed)
		elif test "$board" = "C1" -o "$board" = "D1"; then
			if test "$fan" -eq 0; then
				fan=0
				fanv="Off"
			elif test "$fan" -le 400; then
				fan=50
				fanv="Low"
			else
				fan=100
				fanv="High"
			fi
		fi
	fi

	mode="Reloaded"
	if isflashed; then
		mode="Flashed"	
	fi

	if test -s $SERRORL; then
		cat<<-EOF
			<fieldset><legend><font color=red><strong>Errors</strong></font></legend>
			<form action="/cgi-bin/sys_utils_proc.cgi" method="post">
			<p>Examine and Clear the error messages:
			<input type=submit name="logaction" value="/var/log/systemerror.log">
			</form> 
			<ul>$(cat $SERRORL)</ul>
			</fieldset><br>
		EOF
	fi

	cat<<-EOF
		<fieldset><legend><strong>System</strong></legend>
		<table><tr>
			<td><strong>Temperature</strong> $(drawbargraph $temp $tempv )</td>
			<td><strong>Fan speed</strong> $(drawbargraph $fan $fanv)</td>
			<td><strong>Load</strong> $(drawbargraph $load $loadv)</td>
			<td><strong>CPU</strong> $(drawbargraph $cpu)</td>
			<td><strong>Swap</strong> $(drawbargraph $swap $swapv)</td>
		</tr><tr><td></td></tr><tr>
			<td><strong>Name:</strong> $(hostname -s)</td>
			<td colspan=2><strong>Device:</strong> $device</td>
			<td><strong>Mode:</strong> $mode</td>
		</tr><tr>
			<td colspan=3><strong>Date:</strong> $(date)</td>
			<td colspan=2><strong>Uptime:</strong> $up</td>
		</tr></table></fieldset>
	EOF
}

network_st() {
	Mode=$(cat /sys/class/net/eth0/duplex)
	MTU=$(cat /sys/class/net/eth0/mtu)
#	MAC=$(cat /sys/class/net/eth0/address)
#	Tx=$(cat /sys/class/net/eth0/statistics/tx_bytes)
#	Rx=$(cat /sys/class/net/eth0/statistics/rx_bytes)

	eval $(ifconfig eth0 | awk \
			'/RX bytes/ {printf "Rx=\"%s%s\";", $3, $4} \
			/TX bytes/ {printf "Tx=\"%s%s\";", $7, $8} \
			/inet6/ { if (! match($3, "^fe80:")) ipv6=$3"; "ipv6} \
			/inet addr/{printf "IP=\"%s\";", substr($2,6)} \
			END {printf "ipv6=\"%s\"", ipv6}' | tr "()" "  ")

	if test -n "$ipv6"; then
		IPV6="<br><strong> IPv6: </strong> $ipv6"
	fi

	cat<<-EOF
		<fieldset><legend><strong>Network</strong></legend>
		<strong>Speed: </strong> $(cat /sys/class/net/eth0/speed)Mbps
		<strong>Duplex: </strong> $Mode
		<strong>MTU: </strong> $MTU
		<strong>TX: </strong> $Tx
		<strong>Rx: </strong> $Rx
		<strong>IP: </strong> $IP
		$IPV6
		</fieldset>
	EOF
}

disks_st() {
	if ! has_disks; then
		return 0
	fi

	cat<<-EOF
		<fieldset><legend><strong>Disks</strong></legend>
		<table><tr align=center><th align=left>Bay</th>
		<th>Dev.</th>
		<th>Model</th>
		<th>Capacity</th>
		<th>Power Status</th>
		<th>Temp</th>
		<th>Health</th>
		</tr>
	EOF

	for i in /dev/sd?; do
		dsk=$(basename $i)

		temp="--"; fam=""; mod="None"; tcap=""; pstatus="--"; health_st="--"
		disk_details $dsk

		smartctl -n standby -iAH $i >& /tmp/smt_$dsk

		eval $(awk -v st=$? '
			/^194/ { printf "temp=\"%d\";", $10}
			/not support SMART|Device is in/ {
				print "health_st=\"--\";"
				if (st == 2) print "pstatus=\"standby\";"}
			/SMART overall-health/ {
				if (st == 0) color="black"
				else if  (st == 32) color="blue"
				else color="red"
				printf "health_st=\"<font color=%s>%s</font>\";", color, tolower($NF) }
			/Power mode is:/ { printf "pstatus=\"%s\";", 
				tolower(substr($0, index($0,":")+2))} ' /tmp/smt_$dsk)
		rm -f /tmp/smt_$dsk

		if isnumber $temp; then
			temp="${temp}&deg;C/$(celtofar $temp)&deg;F"
		fi

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

	done
	echo "</table></fieldset>"
}

raid_st() {
	if ! grep -q ARRAY /etc/mdadm.conf 2>/dev/null; then
		return 0
	fi

	cat<<-EOF
		<fieldset><legend><strong>RAID</strong></legend>
		<table><tr align=center>
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
		# if test "$state" = "clear"; then continue; fi

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
					compl=$(drawbargraph $(awk '{printf "%d", $1 * 100 / $3}' /sys/block/$mdev/md/sync_completed))
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
			<td align=left>$compl</td>
			<td>$exp</td>
			</tr>
		EOF
	done
	echo "</table></fieldset>"
}

filesys() {
	dsk="$1"
	dev=$(basename $dsk)
	dname=$dev
	# show LV name?
	if test ${dev:0:3} = "dm-"; then
		dname=$(cat /sys/block/$dev/dm/name)
	fi

	cnt=""; dirty=""; days="";
	cap=0; free=0; perc=0
	
	if test -b $dsk; then
		eval $(df -h $dsk | awk '/'$dev'/{printf "cap=%s;free=%s;perc=%d", $2, $4, $5}')
		type=$(blkid -s TYPE -o value $dsk)
		lbl="$(plabel $dsk)"

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
		for (i=1;i<=n;i++) {
			if (a[i] == "ro") {
				printf ("<font color=red> %s </font>", toupper(a[i])); exit }
			else if(a[i] == "rw") {
				print toupper(a[i]); exit }
		}
	} ' /proc/mounts)"

	cat<<-EOF
		<tr>
		<td>$dname</td>
		<td>$lbl</td>
		<td align=right>${cap}B</td>
		<td>$(drawbargraph $perc ${free}B)</td>
		<td>$type</td>
		<td>$MD</td>
		<td><font color=RED>$dirty</font> </td>
		<td>$cnt $days</td>
		</tr>
	EOF
}

mounted_filesystems_st() {
	if ! grep -q '^/dev/\(sd\|md\|dm-\)' /proc/mounts; then
		return 0
	fi

	cat<<-EOF
		<fieldset><legend><strong>Mounted Filesystems</strong></legend>
		<table><tr align=center>
		<th>Dev.</th>
		<th>Label</th>
		<th>Capacity</th><th>Available</th>
		<th>FS</th><th>Mode</th>
		<th>Dirty</th><th>Automatic FSCK in</th> 
		</tr>
	EOF

	for dsk in $(cut -d" " -f1 /proc/mounts | grep '^/dev/\(sd\|md\|dm-\)' | sort -u); do
		filesys $dsk
	done

	echo "</table></fieldset>"
}

mounted_remote_filesystems_st() {
	if ! grep -q '\(nfs \|cifs\)' /proc/mounts; then
		return 0
	fi

	cat<<-EOF
		<fieldset><legend><strong>Mounted Remote Filesystems</strong></legend>
		<table><tr align=center>
		<th>Host</th>
		<th>Remote Share</th>
		<th>Local Folder</th>
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
			# "df" breaks lines when they are long, usernames can have spaces
			eval $(df -h "$mnt" | grep -v Filesystem | tr -d '\n' | awk '{bs=NF-4; printf "sz=%sB; avai=%sB; perc=%d", $bs, $(bs+2), $(bs+3)}')
			echo "<tr><td>$rrhost</td>
				<td>$rrdir</td>
				<td>$mnt</td>
				<td>$sz</td>
				<td>$(drawbargraph $perc $avai)</td>
				<td>$fs</td></tr>"
		fi
	done < /proc/mounts
	echo "</table></fieldset>"
}

remotely_mounted_filesystems_st() {
	smbm="$(smbstatus -S 2> /dev/null | tail -n +4)"
	nfsm="$(showmount --no-headers --all 2> /dev/null)"

	if test -z "$smbm" -a -z "$nfsm"; then
		return 0
	fi

	cat<<-EOF
		<fieldset><legend><strong>Remotely Mounted Filesystems</strong></legend>
		<table><tr align=center>
		<th>Host</th>
		<th>Share</th>
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
				if ! th=$(awk '/^'$host'[[:space:]]+/{print $3; exit 1}' /etc/hosts); then
					host=$th
				fi
			fi
			echo "<tr><td>$host</td><td>$dir</td><td>nfs</td></tr>"
		done
		IFS=" "
	fi
	echo "</table></fieldset>"
}

backup_st() {
	if ! test -e /var/run/backup.pid; then
		return 0
	fi

	bpid=$(cat /var/run/backup.pid)
	if ! kill -0 $bpid >& /dev/null; then
		rm /var/run/backup.pid
		return
	fi

	cat<<-EOF
		<fieldset><legend><strong>Backup</strong></legend>
		<table><tr><th>ID</th><th>Type</th><th>Folder</th><th>State</th></tr>
	EOF

	for i in /tmp/backup-state.*; do
		id=${i##*.}
		if ! grep -q "^$id;" /etc/backup.conf; then
			rm $i
			continue
		fi

		st=$(cat $i)
		bdir=$(grep ^$id /etc/backup.conf | cut -d";" -f6)
		type=$(grep ^$id /etc/backup.conf | cut -d";" -f2)
		if test "$st" = "In progress"; then
			st="<font color=red>In progress</font>"
		fi
		echo "<tr><td>$id</td><td>$type</td><td>$bdir</td><td align=center>$st</td></tr>"
	done

	echo "</table></fieldset>"
}

filesystem_maintenance_st() {
	if ! test -n "$(ls /tmp/check-* /tmp/format-* /tmp/convert-* /tmp/shrink-* \
		/tmp/enlarg-* /tmp/wip-* 2> /dev/null)"; then
		return 0
	fi

	cat<<-EOF
		<fieldset><legend><strong>Filesystem Maintenance</strong></legend>
		<table><tr><th>Dev.</th><th>Label</th><th>Operation</th></tr>
	EOF

	for j in /dev/sd[a-z][1-9] /dev/md[0-9]* /dev/dm-*; do
		part=$(basename $j)
		fs_progress $part # global ln
		if test -n "$ln"; then
			cat<<-EOF
				<tr><td>$part</td><td>$(plabel $part)</td>
				<td><font color=RED>$ln</font></td></tr>
			EOF
		fi
	done
	echo "</table></fieldset>"
}

printers_st() {
	if ! test -f /etc/printcap -a -n "$(grep '^[^#]' /etc/printcap 2> /dev/null)"; then
		return 0
	fi

	cat<<-EOF
		<fieldset><legend><strong>Printers</strong></legend>
		<table><tr align=center><th>Name</th><th>Model</th><th>Jobs</th></tr>
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
	echo "</table></fieldset>"
}

if test -n "$QUERY_STRING"; then
	parse_qstring
fi

SERRORL=/var/log/systemerror.log

if test -n "$refresh"; then
	html_header
	eval ${refresh}_st
	echo "</body></html>"
	exit 0
fi

ver="$(cat /etc/Alt-F)"
write_header "Alt-F $ver Status Page"
jscripts

mktt st_tt "Checking this will refresh different sections in the page every 10 to 20 seconds.<br>
This consumes CPU, so if you are waiting for something lengtly to accomplish<br>
it will actually take more time if autorefresh is enabled."

launch systems
launch network
launch disks
launch raid
launch mounted_filesystems
launch mounted_remote_filesystems
launch remotely_mounted_filesystems
launch backup
launch filesystem_maintenance
launch printers

cat<<EOF
	<form action="">
Autorefresh <input type=checkbox name="arefresh" value="yes" onclick="frefresh(this)" $(ttip st_tt)>
	</form></body></html>
EOF
