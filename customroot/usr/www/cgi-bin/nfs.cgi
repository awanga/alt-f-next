#!/bin/sh

# cnt, share, host, opts
spit_exports() {
	cnt=$1
	share=$2
	host=$3
	opts=$4
	cat<<-EOF
		<tr><td align=center><input type=checkbox $sel name=xcmtd_$cnt value="#"></td>
		<td><input type=text size=10 id=dir_$cnt name=exp_$cnt value="$share"></td>
		<td><input type=button onclick="browse_dir_popup('dir_$cnt')" value=Browse></td>
		<td><input type=text size=10 id=aip_$cnt name=ip_$cnt value="$host" onclick="def_aip('aip_$cnt','$def_ip')"></td>
		<td><input type=text size=40 id=expopts_$cnt name=xopts_$cnt value="$opts" onclick="def_opts('xpt', 'expopts_$cnt')"></td>
		<td><input type=button value=Browse onclick="opts_popup('expopts_$cnt', 'nfs_exp_opt')"></td>
		</tr>
	EOF
}

# cnt, line
exports_row() {
	cnt=$1
	ln=$2

	# read continuation line, if necessary (read -r can't be used at main, path_escaped chars)
	lnl=$((${#ln}-1))
    if test "${ln:$lnl}" = "\\"; then
        read t
        ln="${ln:0:$lnl} $t"
    fi

	# remove spaces after comment sign
	ln=$(echo $ln | sed 's/#[[:space:]]*/#/')

	echo "$ln" | while read -r share rest; do

		# global share comment
		if test "${share:0:1}" = "#"; then
			sel="checked"
			share=${share:1}
		else
			sel=""
		fi
		
		share=$(path_unescape $share)
		share=$(httpd -e "$share")

		for i in $rest; do
			cnt=$((cnt+1))
			host=$(echo $i | sed -e 's/\(.*\)(.*/\1/') # FIXME: no (opts)
			opts=$(echo $i | sed -e 's/.*(\(.*\))/\1/') # FIXME: no (opts)
			if test "${host:0:1}" = "#"; then
				sel="checked"
				host=${host:1}
			fi
			spit_exports "$cnt" "$share" "$host" "$opts"
		done
		return $cnt # trick to return value from subshell
	done    
}

# fstab_rows ln cnt
fstab_row() {
	local ln cnt hostdir mdir rhost rdir opts nfs
	ln=$1; cnt=$2

	eval $(echo $ln | awk '$3 == "nfs" {printf "nfs=1; hostdir=\"%s\"; mdir=\"%s\"; opts=%s", $1, $2, $4}')
	eval $(echo "$hostdir" | awk -F":" '{printf "rhost=\"%s\"; rdir=\"%s\"", $1, $2}')

	rdir=$(path_unescape $rdir)
	rdir=$(httpd -e "$rdir")
	mdir=$(path_unescape $mdir)
	smdir=$mdir
	mdir=$(httpd -e "$mdir")

	rrhost=${rhost#\#} # remove possible comment char FIXME more than one and space
	cmtd=${rhost%%[!#]*} # get possible comment char FIXME more than one and space
	if test -n "$cmtd"; then sel=checked; else sel=""; fi

	mntfld="<td></td>"
	if test -n "$mdir"; then
		op="Mount"
		if mount -t nfs | grep -q "$smdir"; then
			op="unMount"
		fi
		mntfld="<td><input type=submit value=\"$op\" name=\"$mdir\" onclick=\"return check_dis('$sel','$op')\"></td>"
	fi

	cat<<EOF
		<tr>
		<td align=center><input type=checkbox $sel id=fcmtd_$cnt name=fcmtd_$cnt value="#" onclick="return check_mount('$op','fcmtd_$cnt')"></td>
		$mntfld
		<td><input type=text size=10 id=rhost_$cnt name=rhost_$cnt value="$rrhost"></td>
		<td><input type=text size=12 id=rdir_$cnt name=rdir_$cnt value="$rdir"></td>
		<td><input type=button value=Browse onclick="browse_nfs_popup('rhost_$cnt', 'rdir_$cnt')"></td>
		<td><input type=text size=12 id=mdir_$cnt name=mdir_$cnt value="$mdir"></td>
		<td><input type=button value=Browse onclick="browse_dir_popup('mdir_$cnt')"></td>
		<td><input type=text size=20 id=mntopts_$cnt name=mopts_$cnt value="$opts" onclick="def_opts('mnt', 'mntopts_$cnt')"></td>
		<td><input type=button value=Browse onclick="opts_popup('mntopts_$cnt', 'nfs_mnt_opt')"></td>
		</tr>
EOF
}

. common.sh
check_cookie
read_args
write_header "NFS Setup"

#debug

CONFX=/etc/exports
CONFT=/etc/fstab
CONFM=/etc/misc.conf

if test -f $CONFM; then
	. $CONFM
fi

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
		function opts_popup(id, kind) {
			eopts=document.getElementById(id).value
			window.open("browse_opts.cgi?id=" + id + "?kind=" + kind + "?eopts=" + eopts, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function def_aip(id, def_ip) {
			var opts = document.getElementById(id);
			if (opts.value != "")
				return
			else
				//opts.value = def_ip
				opts.value = "*"
		}
		function def_opts(kind, id) {
			var opts = document.getElementById(id);
			if (opts.value != "")
				return;
			if (kind == "xpt")
				opts.value = "rw,no_root_squash,no_subtree_check,anonuid=99,anongid=98"; // keep in sync with nfs_proc.cgi
			else if (kind == "mnt")
				opts.value = "rw,hard,intr,proto=tcp"; // keep in sync with nfs_proc.cgi
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

	<form name=expdir action=nfs_proc.cgi method="post" >
		<fieldset>
		<legend>Folders to export to other hosts</legend>
		<table>
		<tr align=center>
		<th>Disable</th>
		<th>Folder</th>
		<th>Search</th>
		<th>Allowed hosts</th>
		<th>Export Options</th>
		<th>Options</th>
		</tr>
EOF

hostip=$(hostname -i)
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK
def_ip="$NETWORK/$netmask"

cnt=0
if test -e $CONFX; then
  while read -r ln; do
	if test -z "$ln"; then continue; fi
    exports_row $cnt "$ln"
    cnt=$?
  done < $CONFX
fi

for i in $(seq $((cnt+1)) $((cnt+3))); do
	spit_exports $i
done

cat<<-EOF
	</table><input type=hidden name="n_exports" value="$cnt">
	</fieldset>
	<fieldset>
	<legend>Folders to import from other hosts</legend>
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
		fstab_row "$ln" $cnt
		cnt=$((cnt+1))
	fi	
done < $CONFT

i=$cnt
for i in $(seq $cnt $((cnt+2))); do
	fstab_row "" $i	# ln cnt
done
	
cat<<-EOF
	</table>
	<input type=hidden name="n_fstab" value="$cnt">
	</fieldset>	
EOF

if ! aufs.sh -s >& /dev/null; then
	dnfs_dis="disabled"	
fi

if test -n "$DELAY_NFS"; then
	dnfs_chk="checked"
fi

if test -n "$CLEAN_STALE_NFS"; then
	rmtab_chk="checked"
fi

mktt dnfs_tt "Delay NFS start on boot until the Alt-F packages folder becomes available"
mktt rmtab_tt "Remove remote mount entries at service start."

cat<<-EOF
	<table>
	<tr><td>Delay NFS start on boot</td><td><input $dnfs_dis $dnfs_chk type=checkbox name=delay_nfs value=yes $(ttip dnfs_tt)></td></tr>
	<tr><td>Clean stale entries</td><td><input type=checkbox $rmtab_chk name=clean_rmtab value=yes $(ttip rmtab_tt)></td></tr>
	</table>
	<p><input type="submit" name="submit" value="Submit">$(back_button)
	</form></body></html>
EOF

exit 0

