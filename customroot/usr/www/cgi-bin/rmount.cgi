#!/bin/sh

# fstab_row ln cnt fstype
fstab_row() {
	local ln fstype cnt hostdir mdir rhost rdir opts
	ln=$1; cnt=$2; fstype=$3

	eval $(echo $ln | awk '{
		printf "hostdir=\"%s\"; mdir=\"%s\"; opts=%s", $1, $2, $4}')

	if test "$fstype" = "nfs"; then
		eval $(echo "$hostdir" | awk -F":" '{printf "rhost=\"%s\"; rdir=\"%s\"", $1, $2}')
		nsfopt_but="<td><input type=button value=Browse onclick=\"opts_popup('mntopts_$cnt', 'nfs_mnt_opt')\"></td>"
		browse_but="<td><input type=button value=Browse onclick=\"browse_nfs_popup('rhost_$cnt', 'rdir_$cnt')\"></td>"
	elif test "$fstype" = "cifs"; then
		eval $(echo $hostdir | awk -F"/" '{printf "rhost=\"%s\"; rdir=\"%s\"", $3, substr($0, index($0,$4))}')
		nsfopt_but=""
		browse_but="<td><input type=button value=Browse onclick=\"browse_cifs_popup('rhost_$cnt', 'rdir_$cnt')\"></td>"
	else
		return
	fi

	rdir=$(path_unescape $rdir)
	rdir=$(httpd -e "$rdir")
	mdir=$(path_unescape $mdir)
	edir=$(httpd -e "$mdir")

	rrhost=${rhost#\#} # remove possible comment char
	cmtd=${hostdir%%[!#]*} # get possible comment char
	if test -n "$cmtd"; then dis_chk=checked; else dis_chk=""; fi

	mntfld="<td></td>"
	if test -n "$mdir"; then
		op="Mount"
		if mount -t $fstype | grep -q "$mdir"; then
			op="unMount"
		fi
		mntfld="<td><input type=submit value=\"$op\" name=\"$edir\" onclick=\"return check_dis('$dis_chk','$op')\"></td>"
	fi

	cat<<EOF
		<tr>
		<td align=center><input type=checkbox $dis_chk id=fcmtd_$cnt name=fcmtd_$cnt value="#" onclick="return check_mount('$op','fcmtd_$cnt')"></td>
		$mntfld
		<td><input type=text size=10 id=rhost_$cnt name=rhost_$cnt value="$rrhost"></td>
		<td><input type=text size=12 id=rdir_$cnt name=rdir_$cnt value="$rdir"></td>
		$browse_but
		<td><input type=text size=12 id=mdir_$cnt name=mdir_$cnt value="$edir"></td>
		<td><input type=button value=Browse onclick="browse_dir_popup('mdir_$cnt')"></td>
		<td><input type=text size=20 id=mntopts_$cnt name=mopts_$cnt value="$opts" onclick="def_opts('$fstype', 'mntopts_$cnt')"></td>
		$nsfopt_but
		<td><input type=hidden name=fstype_$cnt value="$fstype"></td>
		</tr>
EOF
}

. common.sh
check_cookie
read_args
write_header "Remote NFS and CIFS Imports Setup"

#debug

CONFT=/etc/fstab
CONFM=/etc/misc.conf

if test -f $CONFM; then
	. $CONFM
fi

if ! aufs.sh -s >& /dev/null; then
	dnfs_dis="disabled"	
fi

if test -n "$DELAY_NFS"; then
	dnfs_chk="checked"
fi

mktt dnfs_tt "Delay NFS start on boot until the Alt-F packages folder becomes available"

cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
		    start_dir = document.getElementById(input_id).value;
		    if (start_dir == "")
		    	start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function browse_nfs_popup(host_id, dir_id) {
			window.open("browse_nfs.cgi?id1=" + host_id + "?id2=" + dir_id, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function browse_cifs_popup(host_id, dir_id) {
			window.open("browse_cifs.cgi?id1=" + host_id + "?id2=" + dir_id, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
        }
		function opts_popup(id, kind) {
			eopts=document.getElementById(id).value
			window.open("browse_opts.cgi?id=" + id + "?kind=" + kind + "?eopts=" + eopts, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function def_opts(kind, id) {
			var opts = document.getElementById(id);
			if (opts.value != "")
				return;
			if (kind == "cifs")
				opts.value = "uid=root,gid=users,credentials=/etc/samba/credentials.root,rw,iocharset=utf8,nounix,noserverino,noauto"
			else if (kind == "nfs")
				opts.value = "rw,hard,intr,proto=tcp,noauto"; // keep in sync with nfs_proc.cgi
		}
		function check_mount(op, id) {
			if (op == "unMount" && document.getElementById(id).checked == true) {
				alert("To disable an entry you must first unmount it.")
				return false
			}
			return true
		}
		function check_dis(sel, op) {
			if (sel == "checked" && op == "Mount") {
				alert("To mount an entry you must first enable it and Submit")
				return false
			}
			return true
		}
	</script>

	<form name=expdir action=rmount_proc.cgi method="post" >
	<fieldset>
	<legend>Shares to import from other NFS servers</legend>
	<table>
	<tr align=center>
	<th>Disable</th>
	<th></th>
	<th>Host</th>
	<th>Folder</th>
	<th>Discover</th>
	<th>Local Folder</th>
	<th>Search</th>
	<th>Mount Options</th>
	<th>Options</th>
	</tr>
EOF

cnt=1
while read -r ln; do
	if $(echo "$ln" | grep -q nfs); then
		fstab_row "$ln" $cnt nfs
		cnt=$((cnt+1))
	fi	
done < $CONFT

for i in $(seq $cnt $((cnt+2))); do
	fstab_row "" $i nfs # ln cnt
done
	
cat<<-EOF
	</table>
	<table>
	<tr><td>Delay NFS start on boot</td><td><input $dnfs_dis $dnfs_chk type=checkbox name=delay_nfs value=yes $(ttip dnfs_tt)></td></tr>
	</table>
	</fieldset>
	<fieldset><legend>Shares to import from other CIFS servers</legend>
EOF

if modprobe -D cifs >& /dev/null; then
	cat<<-EOF
		<table>
		<tr align=center>
		<th>Disable</th>
		<th></th>
		<th>Host</th>
		<th>Share</th>
		<th>Discover</th>
		<th>Local Folder</th>
		<th>Search</th>
		<th>Mount Options</th>
		</tr>
	EOF

	cnt=$((i+1))
	while read -r ln; do
		if echo "$ln" | grep -q cifs; then
			fstab_row "$ln" $cnt cifs
			cnt=$((cnt+1))
		fi
	done < $CONFT

	for i in $(seq $cnt $((cnt+2))); do
		fstab_row "" $i cifs
	done

else
	echo "<p>You have to install the kernel-modules package</p>"
fi

cat<<-EOF
	</table><input type=hidden name=cnt value=$i>
	</fieldset>
	<p><input type="submit" name="submit" value="Submit">$(back_button)
	</form></body></html>
EOF

exit 0

