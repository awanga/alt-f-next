#!/bin/sh

. common.sh
check_cookie
write_header "Backup Server Setup"

CONF_BACKUP=/etc/backup.conf

if ! test -h /Backup -a -d "$(readlink -f /Backup)"; then
	cat<<-EOF
		<h4>No Backup folder found, create it on a filesystem<br>
		 big enought to hold all yours backups:</h4>
		<form action="/cgi-bin/backup_proc.cgi" method=post>
	EOF
	select_part
	echo "<input type=submit name=CreateDir value=CreateDir>
		</form></body></html>"
	exit 0
fi

mktt disable_tt "Check to temporarily disable this backup."
mktt id_tt "Backup identifier."
mktt type_tt "Backup source."
mktt runas_tt "Run the backup as the selected user.<br><br>Should be the \"root\" user for local folders, or the<br> user owning the files when the folder is mounted by NFS or Samba." 
mktt host_tt "Computer to backup from."
mktt src_tt "Folder to backup from."
mktt when_tt "Week or Month day(s) to perform the backup.<br><br><strong>Week day</strong>: 0-Sun, 1-Mon, 2-Tue...<br>0,2,4 means Sun, Tue and Thu<br>0-2 means Sun, Mon and Tue<br>* means everyday.<br><br><strong>Month day:</strong> first character must be a 'd',<br> 1 to 31 allowed, same rules as above applies,<br> e.g., 'd1,15' or 'd1-5' or 'd28' are valid.<br><br>No spaces allowed, no checks done"
mktt at_tt "Hour of the day to perform the backup, 0..23.<br><br>Use the same format as in the \"When\" field.<br>You can schedule several backup for the same hour,<br> they will be performed one at a time, sequentially."
mktt rot_tt "After doing this number of backups, start removing the oldest, as needed.<br>0 disables rotation."
mktt now_tt "Perform the backup now.<br>Disabled if the backup is currently being done.<br>You can start several backups."

cat<<EOF
	<script type="text/javascript">
		function typechg(id, cid) {
			obj = document.getElementById(id)
			idx = obj.selectedIndex
			host_id = "host_id_" + cid
			browse_id = "browse_id_" + cid
			if (obj.options[idx].value == "Dir") {
				document.getElementById(host_id).disabled = true
			} else
				document.getElementById(host_id).disabled = false

			if (obj.options[idx].value == "FTP" || obj.options[idx].value == "HTTP" || obj.options[idx].value == "rsync") {
				document.getElementById(browse_id).disabled = true
			} else
				document.getElementById(browse_id).disabled = false
		}
		function browse_dir(eid, sdir) {
			window.open("browse_dir.cgi?id=" + eid + "?browse=" + sdir, "Browse", "scrollbars=yes, width=500, height=500");
			return false
		}
		function browse_popup(type_id, input_id, host_id) {
			obj = document.getElementById(type_id)
			opi = obj.selectedIndex
			if (opi == 0) {
				alert("Select a backup type first")
				return 0
			}

			op = obj.options[opi].value

			if (op == "Dir") {
			    start_dir = document.getElementById(input_id).value;
			    if (start_dir == "")
			    	start_dir="/mnt";
				window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
				return false;
			} else if (op == "NFS") {
				//function browse_nfs_popup(host_id, dir_id) {
				window.open("browse_nfs.cgi?id1=" + host_id + "?id2=" + input_id, "Browse", "scrollbars=yes, width=500, height=500");
				return false;
			} else if (op == "CIFS") {
				//function browse_cifs_popup(host_id, dir_id) {
				window.open("browse_cifs.cgi?id1=" + host_id + "?id2=" + input_id, "Browse", "scrollbars=yes, width=500, height=500");
				return false;
			}
		}
	</script>
EOF

cifs_dis="disabled"
if modprobe -D cifs >& /dev/null; then cifs_dis=""; fi

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

bdir=$(readlink -f /Backup)
cat<<-EOF
	<form name=backup action="/cgi-bin/backup_proc.cgi" method="post">
	<fieldset><legend>Backup Destination Folder</legend>
	Current: <input type=text id="bdir_id" name=bdir value="$bdir">
	<input type=button onclick="browse_dir('bdir_id','$bdir')" value=Browse>
	<input type=submit name=change onclick="return confirm('Your current backup folder will be renamed $bdir-N and a new one created.'+'\n\n' + 'Proceed?')" value=Change>
	</fieldset>
	<fieldset><legend>Backup Setup</legend>
	<table>
	<tr><th>Disable</th><th>ID</th><th>Type</th><th>Run As</th><th>Host</th>
	<th>Folder</th><th>Browse</th><th>When</th><th>At</th><th>Rotate</th><th></th></tr>
EOF

max_id=0
cnt=0

if test -f $CONF_BACKUP; then
	IFS=";"
	while read id type runas host mac srcpath dstpath when at log nlogs rest; do

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

		none_sel=""; dir_sel=""; nfs_sel=""; cifs_sel=""; ftp_sel=""; http_sel=""
		host_dis=""; browse_dis=""
		case $type in
			Dir) dir_sel=selected; host_dis=disabled ;;
			NFS) nfs_sel=selected ;;
			CIFS) cifs_sel=selected ;;
			FTP) ftp_sel=selected; browse_dis=disabled ;;
			HTTP) http_sel=selected; browse_dis=disabled ;;
			rsync) rsync_sel=selected; browse_dis=disabled ;;
			*) none_sel=selected ;;
		esac

		bcknow_dis=""
		if test -e /var/run/backup.pid; then
			if ps | grep "/usr/bin/backup $id" | grep -qv "grep /usr/bin/backup"; then
				bcknow_dis=disabled
			fi
		fi

		sbck_user=$(echo $bck_user | sed 's/value='$runas'/selected value='$runas'/')

		cat<<-EOF
			<tr align=center>
				<td><input type=checkbox $cmtd_chk name=cmtd_$cnt value="#" $(ttip disable_tt)></td>
				<td><span $(ttip id_tt)>$id</span></td>
				<td><select id=type_id_$cnt name=bck_type_$cnt onChange="typechg('type_id_$cnt','$cnt')" $(ttip type_tt)>
					<option $none_sel>Select One</option>
					<option $dir_sel>Dir</option><option $nfs_sel>NFS</option>
					<option $cifs_dis $cifs_sel>CIFS</option><option $ftp_sel>FTP</option>
					<option $http_sel>HTTP</option><option $rsync_sel>rsync</option>
				</select></td>
				<td><select name="bck_user_$cnt" $(ttip runas_tt)>$sbck_user</select></td>
				<td><input type=text $host_dis size=8 id="host_id_$cnt" name="host_$cnt" value="$host" $(ttip host_tt)>
				<input type=hidden name="mac_$cnt" value="$mac"></td>
				<td><input type=text size=20 id="src_id_$cnt" name="src_$cnt" value="$srcpath" $(ttip src_tt)></td>
				<td><input type=button $browse_dis id="browse_id_$cnt" onclick="browse_popup('type_id_$cnt','src_id_$cnt','host_id_$cnt')" value=Browse></td>
				<td><input type=text size=4 name="when_$cnt" value="$when" $(ttip when_tt)></td>
				<td><input type=text size=4 name="at_$cnt" value="$at" $(ttip at_tt)></td>
				<td><input type=text size=4 name="nlogs_$cnt" value="$nlogs" $(ttip rot_tt)></td>
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
			<td><select id="type_id_$i" name="bck_type_$i" onChange="typechg('type_id_$i','$i')" $(ttip type_tt)>
					<option>Select One</option>
					<option>Dir</option><option>NFS</option><option $cifs_dis>CIFS</option>
					<option>FTP</option><option>HTTP</option><option>rsync</option>
			</select></td>
			<td><select name="bck_user_$i" $(ttip runas_tt)>$bck_user</select></td>
			<td><input type=text size=8 id="host_id_$i" name="host_$i" value="" $(ttip host_tt)>
			<input type=hidden name="mac_$i" value=""></td>
			<td><input type=text size=20 id="src_id_$i" name="src_$i" value="" $(ttip src_tt)></td>
			<td><input type=button id="browse_id_$i" value=Browse onclick="browse_popup('type_id_$i','src_id_$i','host_id_$i')"></td>
			<td><input type=text size=4 name="when_$i" value="" $(ttip when_tt)></td>
			<td><input type=text size=4 name="at_$i" value="" $(ttip at_tt)></td>
			<td><input type=text size=4 name="nlogs_$i" value="0"  $(ttip rot_tt)></td>
		</tr>
	EOF
done

cat<<EOF
	</table></fieldset>
	<input type=hidden name=cnt_know value="$i">
	<input type=submit name=submit value=Submit>$(back_button)
	</form></body></html>
EOF
