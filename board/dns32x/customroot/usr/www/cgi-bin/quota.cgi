#!/bin/sh

. common.sh
check_cookie
write_header "Quota Setup"
has_disks
parse_qstring
#debug

CONFP=/etc/passwd

quota_mopts='jqfmt=vfsv0,usrjquota=aquota.user,grpjquota=aquota.group'

cat<<-EOF
	<form name=frm action="/cgi-bin/quota_proc.cgi" method="post">
	<script type="text/javascript">
		function dis_toogle(obj, id) {
			tg = top.content.document.getElementById(id)
			if (obj.checked == true)
				tg.disabled = false
			else
				tg.disabled = true
		}
	</script>
EOF

if test -z "$user" -a -z "$group" -a -z "$admin"; then
	admin=admin
    kind=admin
    targ=admin
fi

if test -n "$admin"; then
	kind=admin
	targ=admin

	echo "<table><tr><th>Dev.</th><th>Label</th><th>Enabled</th><th>Active</th><th>Check</th></tr>"
	fs=$(grep -E '(ext2|ext3|ext4)' /proc/mounts | cut -d" " -f1)

	j=0
	for i in $fs; do
		j=$((j+1))
		part=$(basename $i)
		qm_chk="checked"; qm_dis=""
		if ! grep -q "^$i.*$quota_mopts" /proc/mounts; then
			qm_chk=""; qm_dis="disabled"
		else
			qs_chk="checked"
			if quotaon -p $i >& /dev/null; then
				qs_chk=""
			fi
		fi
		cat<<-EOF
			<tr><td>$part</td><td>$(plabel $part)</td>
			<td align="center"><input $qm_chk type=checkbox name=enable_$j value="$part" onchange="dis_toogle(this, 'chk_$j')"></td>
			<td align="center"><input $qm_dis $qs_chk type=checkbox id="chk_$j" name=active_$j value="$part"></td>
			<td><input $qm_dis type=submit name=$part value=CheckNow onclick="return confirm('This operation takes a long time to accomplish,\n\
as it has to scan all files on the filesystem.\n\n\
It has to be done the first time quotas are enabled,\n\
and periodically afterwards, to ensure consistency.\n\n\
Continue?')"></td></tr>
		EOF
	done

	cat<<-EOF
		</table><br>
		<input type=hidden name=glb_cnt value="$j">
		<input type=submit name=quota_global value="Submit">
		<input type=submit name=quota_rep value="Report">
	EOF

elif test -n "$user" -o -n "$group"; then

	if test -n "$user"; then
		kind=user
		opt="-u"
		targ="$user"
		name=$(awk -F: '/^'$user':/{printf "%s", $5}' $CONFP)
	else
		kind=group
		opt="-g"
		targ="$group"
		name=$group
	fi

	res=$(quota --show-mntpoint -spwv $opt $targ 2> /dev/null)
	if test -n "$res"; then
		cat<<-EOF
			<h3>Quota for $kind "$name"</h3>
			<table><th colspan=2></th><th colspan=3>Space</th><th colspan=3>Files</th><tr>
				<th>Dev.</th><th>Label</th><th>In Use</th><th>Quota</th><th>Limit</th>
			<th>In Use</td><th>Quota</th><th>Limit</th></tr>
		EOF

		i=0
		echo "$res" | tail +3 | while read fs lbl blocks bquota blimit bgrace files fquota flimit fgrace; do
			i=$((i+1))
			fs=$(basename $fs)
			lbl=$(basename $lbl)
			if test "$lbl" = "$fs"; then lbl=""; fi
			berr=""; if echo "$blocks" | grep -q '*'; then berr="class=\"red\""; fi
			ferr=""; if echo "$files" | grep -q '*'; then ferr="class=\"red\""; fi
			cat<<-EOF
				<tr><td><input type=hidden name=fs_$i value="$fs">$fs</td>
					<td>$lbl</td>
					<td $berr>$blocks</td>
					<td><input type=text size=6 name=bquota_$i value="$bquota"></td>
					<td><input type=text size=6 name=blimit_$i value="$blimit"></td>
					<td $ferr>$files</td>
					<td><input type=text size=6 name=fquota_$i value="$fquota"></td>
					<td><input type=text size=6 name=flimit_$i value="$flimit"></td></tr>
			EOF
		done
		echo "</table><br>"
		echo "<input type=submit name=quota_user value="Submit">$(back_button)"
	else
		echo "<p>You have to setup Disk Quotas first.</p>$(back_button)"
	fi
fi

cat<<-EOF
	
	<input type=hidden name=kind value="$kind">
	<input type=hidden name=targ value="$targ">
	<input type=hidden name=opt value="$opt">
	</form></body></html>
EOF
