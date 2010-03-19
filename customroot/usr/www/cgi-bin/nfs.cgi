#!/bin/sh

# edir ln cnt
exports_row() {
	local edir ln cnt aip opts lopts
	edir=$1; ln=$2; cnt=$3
 
	lopts="";
	RO_SEL=""; RW_SEL=""; SYNC_SEL=""; ASYNC_SEL="";
 	RS_SEL=""; NRS_SEL=""; AS_SEL=""; NAS_SEL="";
 	
	eval $(echo $ln | tr '()' '|' | awk -F'|' '{printf "aip=%s; opts=%s", $1, $2}')
	for i in $(echo $opts | tr ',' ' '); do
		case $i in
			ro)	RO_SEL="SELECTED" ;;
			rw) RW_SEL="SELECTED" ;;
			sync) SYNC_SEL="SELECTED" ;;
			async) ASYNC_SEL="SELECTED" ;;
			root_squash) RS_SEL="SELECTED" ;;
			no_root_squash) NRS_SEL="SELECTED" ;;
			all_squash) AS_SEL="SELECTED" ;;
			no_all_squash) NAS_SEL="SELECTED" ;;
			*) if test -z "$lopts"; then lopts="$i"; else lopts="$lopts,$i";fi ;;
		esac
	done

	exdir=${edir#\#} # remove possible comment char FIXME more than one and space
	cmtd=${edir%%[!#]*}	# get possible comment char FIXME more than one and space
	if test -n "$cmtd"; then sel=CHECKED; else sel=""; fi

	cat<<EOF
		<tr><td><input type=checkbox $sel name=xcmtd_$cnt value="#"></td>
		<td><input type=text size=10 id=dir_$cnt name=exp_$cnt value=$exdir></td>
		<td><input type=button onclick="browse_dir_popup('dir_$cnt')" value=Browse></td>
		<td><input type=text size=10 name=ip_$cnt value=$aip></td>
		<td><select name=rd_$cnt>
			<option value=ro $RO_SEL >Read</option>
			<option value=rw $RW_SEL >RD/WR</option>
		</select></td>
		<td><select name=mode_$cnt>
			<option value=async $ASYNC_SEL >async</option>
			<option value=sync $SYNC_SEL>sync</option>
		</select></td>
		<td><select name=perm_$cnt>
			<option value=no_all_squash $NAS_SEL>def. mapping</option>
			<option value=root_squash $RS_SEL>root to anon.</option>
			<option value=no_root_squash $NRS_SEL>root to root</option>
			<option value=all_squash $AS_SEL>all to anon.</option>
		</select></td>
		<td><input type=text size=20 name=xopts_$cnt value=$lopts></td>
		</tr>
EOF
}

# fstab_rows ln cnt
fstab_row() {
	local ln cnt hostdir mdir rhost rdir opts nfs
	ln=$1; cnt=$2

	eval $(echo $ln | awk '$3 == "nfs" {printf "nfs=1; hostdir=%s; mdir=%s; opts=%s", $1, $2, $4}')
	eval $(echo $hostdir | awk -F":" '{printf "rhost=%s; rdir=%s", $1, $2}')

	rrhost=${rhost#\#} # remove possible comment char FIXME more than one and space
	cmtd=${rhost%%[!#]*}	# get possible comment char FIXME more than one and space
	if test -n "$cmtd"; then sel=CHECKED; else sel=""; fi

	cat<<EOF
		<tr>
		<td><input type=checkbox $sel name=fcmtd_$cnt value="#"></td>
		<td><input type=text size=10 id=rhost_$cnt name=rhost_$cnt value=$rrhost></td>
		<td><input type=text size=12 id=rdir_$cnt name=rdir_$cnt value=$rdir></td>
		<td><input type=button value=Browse onclick="browse_nfs_popup('rhost_$cnt', 'rdir_$cnt')"></td>
		<td><input type=text size=12 id=mdir_$cnt name=mdir_$cnt value=$mdir></td>
		<td><input type=button value=Browse onclick="browse_dir_popup('mdir_$cnt')"></td>
		<td><input type=text size=20 id=fopts_$cnt name=fopts_$cnt value=$opts></td>
		<td><input type=button value=Browse onclick="opts_popup('fopts_$cnt', 'nfs_mnt_opt')"></td>
		</tr>
EOF
}

. common.sh
check_cookie
read_args
write_header "NFS Setup"

#echo "<pre>$(set)</pre>"

CONFX=/etc/exports
CONFT=/etc/fstab

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
	</script>

	<form name=expdir action=nfs_proc.cgi method="post" >
		<fieldset>
		<legend><strong>Directories to export to other hosts</strong></legend>
		<table>
		<tr align=center><td>Disable</td><td>Directory</td><td></td><td>Allowed hosts</td><td></td><td></td><td>User Mapping</td><td>Other Options</td></tr>
EOF

cnt=1
if test -e $CONFX; then
  while read edir ln; do
    exports_row $edir $ln $cnt	# edir ln cnt
    cnt=$((cnt+1))
  done < $CONFX
fi

for i in $(seq $cnt $((cnt+2))); do
	exports_row "" "" $i	# edir ln cnt
done

#rpcinfo to browse net, showmount to browse host

cat<<-EOF
	<input type=hidden name="n_exports" value="$cnt">
	</table></fieldset>
	<fieldset>
	<legend><strong>Directories to import from other hosts</strong></legend>
	<table>
	<tr align=center>
	<td>Disable</td>
	<td>Host</td>
	<td>Directory</td>
	<td>Discover</td>
	<td>Local dir</td>
	<td>Browse</td>
	<td>Mount Options</td>
	<td>Browse</td>
	</tr>
EOF

cnt=1
while read ln; do
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
	<input type=hidden name="n_fstab" value="$cnt">
	</table>
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

echo "<input type=submit value=Submit>
	<input type=button name=back value=\"Back\" onclick=\"history.back()\">
	</form></body></html>"
exit 0

