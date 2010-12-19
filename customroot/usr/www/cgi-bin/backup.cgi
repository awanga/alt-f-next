#!/bin/sh

. common.sh
check_cookie
write_header "Backups Setup"

CONF_BACKUP=/etc/backup.conf

if ! test -h /Backup -a -d "$(readlink -f /Backup)"; then
	cat<<-EOF
		<h4>No Backup directory found, create it on a filesystem<br>
		 big enought to hold all yours backups:</h4>
		<form action="/cgi-bin/backup_proc.cgi" method=post>
	EOF
	select_part
	echo "</select><input type=submit name=CreateDir value=CreateDir>
		</form></body></html>"
	exit 0
fi

mktt disable_tt "Check to temporarily disable this backup."
mktt id_tt "Backup identifier."
mktt type_tt "Type of backup.<br>Currently only Directory is supported.<br>You have to mount NFS or CIFS directories yourself.<br>Remote host must be powered on."
mktt runas_tt "Run the backup as the selected user.<br>Should be the user owning the files mounted by NFS or Samba." 
mktt src_tt "Directory to backup from."
mktt when_tt "Week day(s) to perform the backup.<br>0-Sun, 1-Mon, 2-Tue...<br>0,2,4 means at Sun, Tue and Thu<br>0-2 means at Sun, Mon and Tue<br>* means everyday.<br>No spaces allowed."
mktt at_tt "Hour of the day to perform the backup, 0..23.<br>Use same format as When.<br>You can schedule several backup for the same hour,<br> they will be performed one at a time, sequentially."
mktt rot_tt "After doing this number of backups, start removing the oldest, as needed.<br>0 disables rotation."
mktt log_tt "After doing a backup generates a log with added, removed and changed files.<br>If no changes were detected, the backup is removed.<br>It is too sloow, use only for special directories."
mktt now_tt "Perform the backup now.<br>Disabled if the backup is currently being done.<br>You can start several backups."

cat<<EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
		    start_dir = document.getElementById(input_id).value;
		    if (start_dir == "")
		    	start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
	</script>
	<form action="/cgi-bin/backup_proc.cgi" method=post>
EOF

bck_type="<option>Dir</option><option disabled>NFS</option>
<option disabled>CIFS</option><option disabled>rsync</option>
<option disabled>FTP</option><option disabled>HTTP</option>"

bck_user="<option>root</option>"
OIFS="$IFS"
IFS=":"
while read nick d1 uid d2 uname rest; do
	if test "${nick:0:1}" = "#"; then continue; fi
	if ! id $nick > /dev/null 2>&1; then continue; fi
	if test "$uid" -ge 100; then
		bck_user="${bck_user}<option value=$nick>$uname</option>"
	fi
done < /etc/passwd

cat<<-EOF
	<form name=hosts action=backup_proc.cgi method=post>
	<table>
	<tr align=center><th>Disable</th><th>ID</th><th>Type</th><th>Run As</th><th>Source</th>
	<th>Browse</th><th>When</th><th>At</th><th>Rotate</th><th>Log</th></tr>
EOF

max_id=0
cnt=0

if test -f $CONF_BACKUP; then
	IFS=";"
	while read id type runas srcpath dstpath when at log nlogs rest; do

		cmtd_chk=""
		if test "${id:0:1}" = "#"; then # FIXME, no space allowed
			id=${id:1}
			cmtd_chk="checked"
		fi

		if ! isnumber "$id"; then continue; fi
		if ! isnumber "$nlogs"; then continue; fi

		if test -z "$type" -o -z "$runas" -o -z "$srcpath" -o -z "$dstpath" \
			-o -z "$when" -o -z "$at" -o -z "$log" -o -z "$nlogs"; then continue; fi

		if test "$id" -gt "$max_id"; then max_id=$id; fi

		bcknow_dis=""
		if test -e /var/run/backup.pid; then
			if ps | grep "/usr/bin/backup $id" | grep -qv "grep /usr/bin/backup"; then
				bcknow_dis=disabled
			fi
		fi

		sbck_user=$(echo $bck_user | sed 's/value='$runas'/selected value='$runas'/')

		log_chk=""; if test "$log" = "yes"; then log_chk="checked"; fi
		cat<<-EOF
			<tr align=center>
				<td><input type=checkbox $cmtd_chk name=cmtd_$cnt value="#" $(ttip disable_tt)></td>
				<td><span $(ttip id_tt)>$id</span></td>
				<td><select name=bck_type_$cnt $(ttip type_tt)>$bck_type</select></td>
				<td><select name=bck_user_$cnt $(ttip runas_tt)>$sbck_user</select></td>
				<td><input type=text size=20 id=src_id_$cnt name=src_$cnt value="$srcpath" $(ttip src_tt)></td>
				<td><input type=button onclick="browse_dir_popup('src_id_$cnt')" value=Browse></td>
				<td><input type=text size=4 name=when_$cnt value="$when" $(ttip when_tt)></td>
				<td><input type=text size=4 name=at_$cnt value="$at" $(ttip at_tt)></td>
				<td><input type=text size=4 name=nlogs_$cnt value="$nlogs" $(ttip rot_tt)></td>
				<td><input type=checkbox $log_chk name=log_$cnt value="yes" $(ttip log_tt)></td>
				<td><input type=submit $bcknow_dis name="$id" value=BackupNow $(ttip now_tt)></td>
			</tr>
		EOF
		cnt=$((cnt+1))
	done < $CONF_BACKUP 
fi

IFS="$OIFS"
for i in $(seq $cnt $((cnt+2))); do
	max_id=$((max_id+1))
	cat<<-EOF
		<tr align=center>
			<td><input type=checkbox name=cmtd_$cnt value="#" $(ttip disable_tt)></td>
			<td><span $(ttip id_tt)>$max_id</span></td>
			<td><select name=bck_type_$i $(ttip type_tt)>$bck_type</select></td>
			<td><select name=bck_user_$i $(ttip runas_tt)>$bck_user</select></td>
			<td><input type=text size=20 id="src_id_$i" name=src_$i value="" $(ttip src_tt)></td>
			<td><input type=button value=Browse onclick="browse_dir_popup('src_id_$i')"></td>
			<td><input type=text size=4 name=when_$i value="" $(ttip when_tt)></td>
			<td><input type=text size=4 name=at_$i value="" $(ttip at_tt)></td>
			<td><input type=text size=4 name=nlogs_$i value="0"  $(ttip rot_tt)></td>
			<td><input type=checkbox name=log_$i value="yes" $(ttip log_tt)></td>
		</tr>
	EOF
done

cat<<EOF
	<tr><td><br></td></br>
	<tr><td colspan=2></td><td colspan=2>
	<input type=hidden name=cnt_know value="$i">
	<input type=submit name=submit value=Submit>$(back_button)
	</td></tr>
	</table></form></body></html>
EOF
