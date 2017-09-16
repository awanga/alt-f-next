#!/bin/sh

. common.sh
check_cookie
write_header "Samba Setup"

CONF_SMB=/etc/samba/smb.conf

mktt proto_tt "SMB1 is the the old MS-Windows protocol and is needed for most embedded devices and linux clients.<br>SMB2 is a newer protocol introduced in MS-Windows Vista but might have compatibility issues.<br>After changing it might be needed to reboot the NAS box and accessing PCs."

if test -e $CONF_SMB; then
	if ! grep -q '^[[:space:]#]*use sendfile' $CONF_SMB; then
		chgfl=1; sed -i '/socket options/a\
	use sendfile = yes' $CONF_SMB
	fi

	if ! grep -q '^[[:space:]#]*log level' $CONF_SMB; then
		chgfl=1; sed -i '/max log size/a\
	log level = 1' $CONF_SMB
	fi

	if ! grep -q '^[[:space:]#]*max protocol' $CONF_SMB; then
		chgfl=1; sed -i '/print command/a\
	max protocol = SMB2' $CONF_SMB
	fi

	if ! grep -q '^[[:space:]#]*min protocol' $CONF_SMB; then
		chgfl=1; sed -i '/print command/a\
	#min protocol = SMB2' $CONF_SMB
	fi
	
	if ! grep -q '^[[:space:]#]*client ipc signing' $CONF_SMB; then
		chgfl=1; sed -i '/print command/a\
	client ipc signing = auto' $CONF_SMB
	fi
	
	if ! grep -q '^[[:space:]#]*client signing' $CONF_SMB; then
		chgfl=1; sed -i '/print command/a\
	client signing = auto' $CONF_SMB
	fi

	if ! grep -q '^[[:space:]#]*server signing' $CONF_SMB; then
		chgfl=1; sed -i '/print command/a\
	\
	server signing = disabled' $CONF_SMB
	fi

	if test -n "$chgflg" && rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi
	
	SMB1_EN_check="checked"
	if grep -q '^[[:space:]]*max protocol = SMB2' $CONF_SMB; then
		SMB2_EN_check="checked"
	fi

	if grep -q '^[[:space:]]*min protocol = SMB2' $CONF_SMB; then
		SMB2_EN_check="checked"
		SMB1_EN_check=""
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
	</script>
	<form id=smbf name=smbf action=smb_proc.cgi method="post">

	<fieldset><legend>Host details</legend><table>
	<tr><td>Host name:</td>
		<td><input readonly type=text name=hostname value="$(hostname -s)"></td><td>Use "Setup Host" to change</td></tr>
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
	<table>
	<tr><td>Enable SMB1</td><td><input type=checkbox $SMB1_EN_check name=enable_smb1 id=enable_smb1 value=yes $(ttip proto_tt)></td></tr>
	<tr><td>Enable SMB2</td><td><input type=checkbox $SMB2_EN_check name=enable_smb2 id=enable_smb2 value=yes $(ttip proto_tt)></td></tr>
	</table>
	</fieldset>
EOF

if grep -q "# Samba config file created using SWAT" $CONF_SMB; then
	swat="<h4 class=\"warn\">The Advanced SWAT configuration tool has been used.<br>
	If you Submit changes, then SWAT changes applied to shares will be lost</h4>"
else
	swat="<p>"
fi

cat<<EOF
	$swat
	<input type=submit name=submit value="Submit">
	<input type=submit name=submit value="Advanced" onClick="return confirm('\
On the next SWAT Authentication dialogue you have to enter' + '\n' +
'\'root\' for the \'User Name\' and the webUI password for \'Password\'.' + '\n\n' +
'Changes made might not be recognized latter in this web page.' + '\n\n' + 'Continue?')">
	$(back_button)
	</form></body></html>
EOF
