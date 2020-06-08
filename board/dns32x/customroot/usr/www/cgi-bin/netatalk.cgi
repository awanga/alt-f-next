#!/bin/sh

. common.sh
check_cookie
write_header "Netatalk Setup"

CONF_NETA=/etc/afp.conf

if grep -q '^\[Homes\]' $CONF_NETA; then
	user_chk="checked"
fi

if grep -q '^[[:space:]]*uam list[[:space:]]*=[^#]*uams_guest.so' $CONF_NETA; then
	guest_chk="checked"
fi

if grep -q '^[[:space:]]*uam list[[:space:]]*=[^#]*uams_clrtxt.so' $CONF_NETA; then
	clrtxt_chk="checked"
fi

if grep -q '^[[:space:]]*uam list[[:space:]]*=[^#]*uams_dhx.so' $CONF_NETA; then
	dhx_chk="checked"
fi

if grep -q '^[[:space:]]*uam list[[:space:]]*=[^#]*uams_dhx2.so' $CONF_NETA; then
	dhx2_chk="checked"
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
		function toogle(cnt) {
			obj = document.getElementById("maxsz_" + cnt)
			obj.disabled = ! obj.disabled
		}
	</script>
	<form id=netaf name=netaf action=netatalk_proc.cgi method="post">
	<fieldset>
	<legend>Folders to share</legend>
	<table>
	<tr>
		<th>Folder</th>
		<th>Browse</th>
		<th>Share Name</th>
		<th>Allow</th>
		<th>Read<br>Only</th>
		<th>Time<br>Machine</th>
		<th>Max Size<br>(MiB)</th>
	</tr>
EOF

awk -F = 'BEGIN {
		t = FS; FS= ":"
		i = 0; users[i++] = "anybody";
		if (system("test -f /etc/samba/smbpasswd") == 0)
			while (getline <"/etc/samba/smbpasswd")
				users[i++] = $1
		while (getline <"/etc/group")
			if ($3 >= 100 || $3 == 34 || $3 == 80) 
				users[i++] = "@" $1
	FS = t
	}
	 /\[.*\]/ {
		parse( pshare($0), $0)
		delete opts
	}
	END {
		for (i=cnt+1; i<cnt+4; i++)
			spit(i, opts)
		printf "</table><input type=hidden name=neta_cnt value=\"%d\">", i
	}

function pshare(line) {
	i = index(line, "[") + 1
	return substr(line, i, index(line, "]") - i)
}

function spit(cnt, opts) {
	
	rdir = rdonly_chk = tm_chk = ""
	sel = "anybody"
	size_dis = "disabled"
	useropt = ""

	if (opts["path"] != "") {
		sprintf("readlink -f \"%s\" ", opts["path"]) | getline rdir
		if (rdir == "") {
			rdir = opts["path"]
		}
		sprintf("httpd -e \"%s\" ", rdir) | getline rdir

		if (opts["valid users"] != "")
			sel = opts["valid users"]

		if (opts["read only"] == "yes")
			rdonly_chk = "checked"

		if (opts["time machine"] == "yes") {
			tm_chk = "checked"
			size_dis = ""
		}
	}

	for (j in users) {
		if (users[j] == sel)
			useropt = useropt "<option selected>" users[j] "</option>"
		else
			useropt = useropt "<option>" users[j] "</option>"
	}

	printf "<tr><td><input type=text size=25 id=ldir_%d name=ldir_%d value=\"%s\"></td>\n", cnt, cnt, rdir
	printf "<td><input type=button onclick=\"browse_dir_popup(%cldir_%d%c)\" value=Browse></td>\n", 047, cnt, 047
	printf "<td><input type=text size=12 name=shname_%d value=\"%s\"></td>\n", cnt, opts["share_name"]
	printf "<td align=center><select name=user_%d>%s</select></td>\n", cnt, useropt
	printf "<td align=center><input %s type=checkbox name=rdonly_%d value=\"yes\"></td>\n", rdonly_chk, cnt 
	printf "<td align=center><input %s type=checkbox name=tm_%d value=\"yes\" onclick=\"toogle(%d)\"></td>\n", tm_chk, cnt, cnt 
	printf "<td><input %s type=text size=4 name=maxsz_%d id=maxsz_%d value=\"%s\"></td>\n", size_dis, cnt, cnt, opts["vol size limit"]
	print "</tr>\n"
}

function parse(share_name, line) {
	if (share_name == "Global" || share_name == "Homes" || index(line,"#"))
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
}' $CONF_NETA

cat<<-EOF
	<p><table>
	<tr><td>Password encryption</td>
		<td>None<input type=checkbox $clrtxt_chk name=clrtxt value="yes">
		Strong<input type=checkbox $dhx_chk name=dhx value="yes">
		Strongest<input type=checkbox $dhx2_chk name=dhx2 value="yes"></td></tr>
	<tr><td>Share users home folder</td><td><input type=checkbox $user_chk name=want_homes value="yes"></td></tr>
	<tr><td>Allow guest login</td><td><input type=checkbox $guest_chk name=allow_guest value="yes"></td></tr>

	</table></fieldset>
	<p><input type=submit name=submit value="Submit">$(back_button)
	</form></body></html>
EOF

