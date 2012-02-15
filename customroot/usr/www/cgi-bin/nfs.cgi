#!/bin/sh

# edir ln cnt
exports_row() {
	local edir ln cnt aip opts lopts
	edir=$1; ln=$2; cnt=$3
 
	lopts="";
 	
	eval $(echo $ln | tr '()' '|' | awk -F'|' '{printf "aip=%s; opts=%s", $1, $2}')

	exdir=${edir#\#} # remove possible comment char FIXME more than one and space
	cmtd=${edir%%[!#]*}	# get possible comment char FIXME more than one and space
	exdir="$(path_unescape $exdir)"

	if test -n "$cmtd"; then sel=checked; else sel=""; fi

	cat<<EOF
		<tr><td align=center><input type=checkbox $sel name=xcmtd_$cnt value="#"></td>
		<td><input type=text size=10 id=dir_$cnt name=exp_$cnt value="$exdir"></td>
		<td><input type=button onclick="browse_dir_popup('dir_$cnt')" value=Browse></td>
		<td><input type=text size=10 id=aip_$cnt name=ip_$cnt value="$aip" onclick="def_aip('aip_$cnt','$def_ip')"></td>
		<td><input type=text size=40 id=expopts_$cnt name=xopts_$cnt value="$opts" onclick="def_opts('xpt', 'expopts_$cnt')"></td>
		<td><input type=button value=Browse onclick="opts_popup('expopts_$cnt', 'nfs_exp_opt')"></td>
		</tr>
EOF
}

# fstab_rows ln cnt
fstab_row() {
	local ln cnt hostdir mdir rhost rdir opts nfs
	ln=$1; cnt=$2

	eval $(echo $ln | awk '$3 == "nfs" {printf "nfs=1; hostdir=\"%s\"; mdir=\"%s\"; opts=%s", $1, $2, $4}')
	eval $(echo "$hostdir" | awk -F":" '{printf "rhost=\"%s\"; rdir=\"%s\"", $1, $2}')

	rdir="$(path_unescape $rdir)"
	mdir="$(path_unescape $mdir)"

	rrhost=${rhost#\#} # remove possible comment char FIXME more than one and space
	cmtd=${rhost%%[!#]*}	# get possible comment char FIXME more than one and space
	if test -n "$cmtd"; then sel=checked; else sel=""; fi

	mntfld="<td></td>"
	if test -n "$mdir"; then
		op="Mount"
		if mount -t nfs | grep -q "$mdir"; then
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
		<legend><strong>Directories to export to other hosts</strong></legend>
		<table>
		<tr align=center>
		<th>Disable</th>
		<th>Directory</th>
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

cnt=1
if test -e $CONFX; then
  while read -r edir ln; do
    exports_row $edir $ln $cnt	# edir ln cnt
    cnt=$((cnt+1))
  done < $CONFX
fi

for i in $(seq $cnt $((cnt+2))); do
	exports_row "" "" $i	# edir ln cnt
done

cat<<-EOF
	</table><input type=hidden name="n_exports" value="$cnt">
	</fieldset><br>
	<fieldset>
	<legend><strong>Directories to import from other hosts</strong></legend>
	<table>
	<tr align=center>
	<th>Disable</th>
	<th></th>
	<th>Host</th>
	<th>Directory</th>
	<th>Discover</th>
	<th>Local dir</th>
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

if false; then
res=$(rpcinfo -b 100005 3 | sort -u  | while read hip hnm; do
	if test $hnm = "(unknown)"; then
		host=$hip
	else
		host=$hnm
	fi
	showmount -e --no-headers $host	| while read hdir rest; do
		echo "<li>$host:$hdir</li>"
	done
done)

echo "<ul> $res </ul>"
fi

if ! aufs.sh -s >& /dev/null; then
	dnfs_dis="disabled"	
fi

if test -n "$DELAY_NFS"; then
	dnfs_chk="checked"
fi

mktt dnfs_tt "Delay NFS start on boot until the Alt-F packages directory becomes available"

cat<<-EOF
	<br>Delay NFS start on boot <input $dnfs_dis $dnfs_chk type=checkbox name=delay_nfs value=yes $(ttip dnfs_tt)>
	<br><input type="submit" name="submit" value="Submit">
	$(back_button)
	</form></body></html>
EOF

exit 0

