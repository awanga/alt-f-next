#!/bin/sh

. common.sh
check_cookie
write_header "Samba Setup"

CONF_SMB=/etc/samba/smb.conf
CONF_FST=/etc/fstab

# fstab_rows ln cnt
fstab_row() {
	local ln cnt hostdir mdir rhost rdir opts nfs
	ln=$1; cnt=$2

	eval $(echo $ln | awk '$3 == "cifs" {
		printf "hostdir=\"%s\"; mdir=\"%s\"; opts=%s", $1, $2, $4}')

	eval $(echo $hostdir | awk -F"/" '{
		printf "rhost=\"%s\"; rdir=\"%s\"", $3, substr($0, index($0,$4))}')

	rdir="$(path_unescape $rdir)"
	rdir=$(httpd -e "$rdir")
	mdir="$(path_unescape $mdir)"
	edir=$(httpd -e "$mdir")

	cmtd=${hostdir%%[!#]*}	# get possible comment char
	if test -n "$cmtd"; then dis_chk=checked; else dis_chk=""; fi

	mntfld="<td></td>"
	if test -n "$mdir"; then
		op="Mount"
		if mount -t cifs | grep -q "$mdir"; then
			op="unMount"
		fi
		mntfld="<td><input type=submit value=\"$op\" name=\"$edir\" onclick=\"return check_dis('$dis_chk','$op')\"></td>"
	fi

	cat<<-EOF
		<tr>
		<td align=center><input type=checkbox $dis_chk id="fstab_en_$cnt" name="fstab_en_$cnt" value="#" onclick="return check_mount('$op','fstab_en_$cnt')"></td>
		$mntfld
		<td><input type=text size=10 id=rhost_$cnt name=rhost_$cnt value="$rhost"></td>
		<td><input type=text size=12 id=rdir_$cnt name=rdir_$cnt value="$rdir"></td>
		<td><input type=button value=Browse onclick="browse_cifs_popup('rhost_$cnt', 'rdir_$cnt')"></td>
		<td><input type=text size=12 id=mdir_$cnt name=mdir_$cnt value="$edir"></td>
		<td><input type=button value=Browse onclick="browse_dir_popup('mdir_$cnt')"></td>
		<td><input type=text size=20 id=mntopts_$cnt name=mopts_$cnt value="$opts" onclick="def_opts('mntopts_$cnt')"></td>
		</tr>
	EOF
}

if test -e $CONF_SMB; then
	if ! grep -q '[[:space:]]*use sendfile' $CONF_SMB; then
		sed -i '/socket options/a\	use sendfile = yes'  $CONF_SMB
	fi

	eval $(awk '/server string/{split($0, a, "= ");
		print "hostdesc=\"" a["2"] "\""}
		/workgroup/{split($0, a, "= ");
		print "workgp=\"" a["2"] "\""}' $CONF_SMB)
else
	hostdesc=""
	workgp=""
fi

if test "$hostdesc" = "NAS"; then
	hostdesc="$(hostname) NAS"
fi

cat<<EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
		    start_dir = document.getElementById(input_id).value;
		    if (start_dir == "")
		    	start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function browse_cifs_popup(host_id, dir_id) {
			window.open("browse_cifs.cgi?id1=" + host_id + "?id2=" + dir_id, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
        }
		function swat_popup() {
			if (confirm("On the next SWAT Authentication dialogue you have to enter\n" + 
				"'root' for the 'User Name' and the web password for 'Password'.\n\n" +
				"Changes made might not be recognized latter in this page.\n\nContinue?")) {
				if (location.protocol == "http:")
					port = ":901";
				else if (location.protocol == "https:")
					port = ":902";
				else
					return;
				window.open(location.protocol + "//" + location.hostname + port, "SWAT", "scrollbars=yes, width=800, height=600");
			}
        }
		function def_opts(id) {
			var opts = document.getElementById(id);
			if (opts.value != "")
				return;
			opts.value = "uid=root,gid=users,credentials=/etc/samba/credentials.root,rw,iocharset=utf8,nounix,noserverino"
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
	<form id=smbf name=smbf action=smb_proc.cgi method="post">

	<fieldset><legend>Host details</legend><table>
	<tr><td>Host name:</td>
		<td><input readonly type=text name=hostname value="$(hostname -s)">Use "Setup Host" to change</td></tr>
	<tr><td>Host description:</td>
		<td><input type=text name=hostdesc value="$hostdesc"></td></tr>
	<tr><td>Workgroup:</td>
		<td><input type=text name=workgp value="$workgp"></td></tr>
	</table></fieldset>

	<fieldset><legend>Folders to export to other hosts</legend>
	<table>
	<tr>
		<th>Disable</th>
		<th>Folder</th>
		<th>Browse</th>
		<th>Share Name</th>
		<th>Comment</th>
		<th>Allow</th>
		<th>Browseable</th>
		<th>Read<br>Only</th>
		<th>Inherit<br>Perms</th>
	</tr>
EOF

awk -F = 'BEGIN {
		t = FS; FS= ":"
		i = 0; users[i++] = "anybody"; users[i++] = "nonpublic"
		if (system("test -f /etc/samba/smbpasswd") == 0)
			while (getline <"/etc/samba/smbpasswd")
				users[i++] = $1
		while (getline <"/etc/group")
			if ($3 >= 100 || $3 == 34 || $3 == 80 || $3 == 84) 
				users[i++] = "+" $1
	FS = t
	}
	 /\[.*\]/ {
		parse( pshare($0), $0)
		delete opts
	}
	END {
		for (i=cnt+1; i<cnt+4; i++)
			spit(i, opts)
		printf "</table><input type=hidden name=smb_cnt value=\"%d\">", i
	}

function pshare(line) {
	i = index(line, "[") + 1
	return substr(line, i, index(line, "]") - i)
}

function spit(cnt, opts) {
	
	rdir = rdonly_chk = dis_chk = browse_chk = inhperms_chk = ""
	rdonly_chk = "checked"
	browse_chk = "checked"
	sel = "nonpublic"
	useropt = ""

	if (opts["path"] != "") {
		sprintf("readlink -f \"%s\" ", opts["path"]) | getline rdir
		if (rdir == "") {
			rdir = opts["path"]
		}
		sprintf("httpd -e \"%s\" ", rdir) | getline rdir
		browse_chk = "checked"
		if (opts["browseable"] == "no")
			browse_chk = ""

		if (opts["valid users"] != "")
			sel = opts["valid users"]
		else if (opts["public"] == "yes" || opts["guest ok"] == "yes")
			sel = "anybody"

		if (opts["read only"] == "no" || opts["read only"] == "No")
			rdonly_chk = ""

		if (opts["available"] == "no")
			dis_chk = "checked"

		if (opts["inherit permissions"] == "yes" || opts["share_name"] == "Public (Read Write)")
			inhperms_chk = "checked"

	} else 
		rdonly_chk = dis_chk = browse_chk = ""

	for (j in users) {
		if (users[j] == sel)
			useropt = useropt "<option selected>" users[j] "</option>"
		else
			useropt = useropt "<option>" users[j] "</option>"
	}

	printf "<tr><td align=center><input type=checkbox %s name=avail_%d value=no></td>", dis_chk, cnt
	printf "<td><input type=text size=16 id=ldir_%d name=ldir_%d value=\"%s\"></td>\n", cnt, cnt, rdir
	printf "<td><input type=button onclick=\"browse_dir_popup(%cldir_%d%c)\" value=Browse></td>\n", 047, cnt, 047
	printf "<td><input type=text size=12 name=shname_%d value=\"%s\"></td>\n", cnt, opts["share_name"]
	printf "<td><input type=text size=16 name=cmt_%d value=\"%s\"></td>\n", cnt, opts["comment"]
	printf "<td align=center><select name=user_%d>%s</select></td>\n", cnt, useropt
	printf "<td align=center><input %s type=checkbox name=browse_%d value=yes></td>\n", browse_chk, cnt
	printf "<td align=center><input %s type=checkbox name=rdonly_%d value=yes></td>\n", rdonly_chk, cnt 
	printf "<td align=center><input %s type=checkbox name=inhperms_%d value=yes></td>\n", inhperms_chk, cnt 
	print "</tr>\n"
}

function parse(share_name, line) {
	if (tolower(share_name) == "global" || tolower(share_name) == "printers")
		next

	cnt++
	delete opts
	opts["share_name"] = share_name 
	while (st = getline) {
		fc = substr($0,1,1)
		if (fc == "#" || fc == ";")
			continue
		if (fc == "[")
			break

		key=$1
		gsub("^( |\t)*|( |\t)*$", "", key)  # remove leading and trailing spaces

		value = substr($0, index($0,$2)) # path can have the '=' char, which is the field separator
		gsub("^( |\t)*|( |\t)*$", "", value)
		opts[key] = value
	}

	spit(cnt, opts)

	if (st == 0)
		return

	parse(pshare($0), $0)
}' $CONF_SMB

cat<<-EOF
	</fieldset>

	<fieldset><legend>Folders to import from other hosts</legend>
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

	cnt=1
	while read -r ln; do
		if echo "$ln" | grep -q cifs; then
			fstab_row "$ln" $cnt
			cnt=$((cnt+1))
		fi
	done < $CONF_FST

	i=$cnt
	for i in $(seq $cnt $((cnt+2))); do
		fstab_row "" $i	# ln cnt
	done

else
	echo "<p>You have to install the kernel-modules package</p>"
fi

if grep -q "# Samba config file created using SWAT" $CONF_SMB; then
	swat="<h4 class=\"warn\">The Advanced SWAT configuration tool has been used.<br>
	If you Submit changes, then SWAT changes applied to shares will be lost</h4>"
else
	swat="<p>"
fi

cat<<EOF
	</table><input type=hidden name=import_cnt value=$i>
	</fieldset>
	$swat
	<input type=submit name=submit value="Submit">
	<input type=button value="Advanced" onClick="return swat_popup()">
	$(back_button)
	</form></body></html>
EOF

