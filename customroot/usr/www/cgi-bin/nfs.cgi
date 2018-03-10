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

. common.sh
check_cookie
read_args
write_header "NFS exports Setup"

#debug

CONFX=/etc/exports
#CONFT=/etc/fstab
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
				opts.value = "rw,hard,intr,proto=tcp,noauto"; // keep in sync with nfs_proc.cgi
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
if test -s $CONFX; then
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
mktt blksz_tt "Applied only on next server start. Use 'auto' to use an automaticaly computed value.<br>Value will be rounded to the near 4KiB boundary. The displayed value is the one currenty in use (not set) value"

curr_blksz=$(cat /proc/fs/nfsd/max_block_size 2>/dev/null)

if test -z "$NFS_BLKSIZE"; then
	NFS_BLKSIZE="auto"
elif test "$curr_blksz" -gt 0 2>/dev/null; then
	if test "$NFS_BLKSIZE" != "$curr_blksz"; then
		dmsg="(set to $NFS_BLKSIZE)"
	fi
	NFS_BLKSIZE=$curr_blksz
fi

cat<<-EOF
	<table>
	<tr><td>Delay NFS start on boot</td><td><input $dnfs_dis $dnfs_chk type=checkbox name=delay_nfs value=yes $(ttip dnfs_tt)></td></tr>
	<tr><td>Clean stale entries</td><td><input type=checkbox $rmtab_chk name=clean_rmtab value=yes $(ttip rmtab_tt)></td></tr>
	<tr><td>Max NFS Block size</td><td><input type=text size=7 name="NFS_BLKSIZE" value="$NFS_BLKSIZE" $(ttip blksz_tt)> $dmsg</td></tr>
	</table>
	<p><input type="submit" name="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
