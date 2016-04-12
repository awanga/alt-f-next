#!/bin/sh

. common.sh
check_cookie
write_header "rsyncd Setup"

mktt rsynci_tt "Inetd mode: rsyncd runs only when necessary, slower to start, conserves memory."
mktt rsyncs_tt "Server mode: rsyncd always running, faster, always consuming memory<br>
(the rsync checkboxes in the inetd web page will be unchecked)."

CONF_RSYNC=/etc/rsyncd.conf
INETD_CONF=/etc/inetd.conf

if grep -q '^rsync' $INETD_CONF; then
	RSYNC_INETD=checked
else
	RSYNC_SERVER=checked
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
	<form id=rsyncf name=rsync action=rsync_proc.cgi method="post">
	<fieldset>
	<legend>Folder Modules</legend>
	<table>
	<tr>
		<th>Disable</th>
		<th>Folder</th>
		<th>Browse</th>
		<th>Module Name</th>
		<th>Comment</th>
		<th>Allow</th>
		<th align=center>Browseable</th>
		<th>Read Only</th>
	</tr>
EOF

awk -F = 'BEGIN {
		t = FS; FS= ":"
		i = 0; users[i++] = "anybody"
		while (getline <"/etc/rsyncd.secrets") {
			if (substr($1,1,1) == "#") continue
			if (system("id " $1 " >& /dev/null") == 0)
				users[i++] = $1
		}
		FS = t
	} 
	/\[.*\]/ {
		parse( pshare($0), $0)
		delete opts
	}
	END {
		for (i=cnt+1; i<cnt+4; i++)
			spit(i, opts)
		printf "</table><input type=hidden name=rsync_cnt value=\"%d\">", i
	}

function pshare(line) {
	i = index(line, "[") + 1
	return substr(line, i, index(line, "]") - i)
}

function spit(cnt, opts) {

	rdir = rdonly_chk = dis_chk = browse_chk = ""
	rdonly_chk = "checked"
	browse_chk = "checked"
	sel = "anybody"
	useropt = ""

	if (opts["path"] != "") {
		sprintf("readlink -f \"%s\" ", opts["path"]) | getline rdir
		if (rdir == "") {
			rdir = opts["path"]
		}
		sprintf("httpd -e \"%s\" ", rdir) | getline rdir
		browse_chk = "checked"
		if (opts["list"] == "no")
			browse_chk = ""
		if (opts["auth users"] != "")
			sel = opts["auth users"]
		if (opts["read only"] == "no")
			rdonly_chk = ""
		if (opts["max connections"] == "-1")
			dis_chk = "checked"
	} else 
		rdonly_chk = dis_chk = browse_chk = ""

	for (j in users) {
		if (users[j] == sel)
			useropt = useropt "<option selected>" users[j] "</option>"
		else
			useropt = useropt "<option>" users[j] "</option>"
	}

	printf "<tr><td align=center><input type=checkbox %s name=avail_%d value=no></td>", dis_chk, cnt
	printf "<td><input type=text id=ldir_%d name=ldir_%d value=\"%s\"></td>\n", cnt, cnt, rdir
	printf "<td><input type=button  onclick=\"browse_dir_popup(%cldir_%d%c)\" value=Browse></td>\n", 047, cnt, 047
	printf "<td><input type=text size=8 name=shname_%d value=\"%s\"></td>\n", cnt, opts["share_name"]
	printf "<td><input type=text name=cmt_%d value=\"%s\"></td>\n", cnt, opts["comment"]
	printf "<td align=center><select name=user_%d>%s</select></td>\n", cnt, useropt
	printf "<td align=center><input %s type=checkbox name=browse_%d value=yes></td>\n", browse_chk, cnt
	printf "<td align=center><input %s type=checkbox name=rdonly_%d value=yes></td>\n", rdonly_chk, cnt 
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

		value=substr($0, index($0,$2)) # path can have the '=' char, which is the field separator
		gsub("^( |\t)*|( |\t)*$", "", value)
		opts[key] = value
	}

	spit(cnt, opts)

	if (st == 0)
		return

	parse(pshare($0), $0)
}' $CONF_RSYNC

cat<<EOF
	</fieldset>
	<table>
		<tr><td>inetd mode</td><td><input type=radio $RSYNC_INETD name=rsync value="inetd" $(ttip rsynci_tt)></td></tr>
		<tr><td>server mode</td><td><input type=radio $RSYNC_SERVER name=rsync value="server" $(ttip rsyncs_tt)></td></tr>
		<tr><td></td><tr>
	</table>
	<input type="hidden" name=from_url value="$HTTP_REFERER">
	<input type=submit name=submit value="Submit">$(back_button)
	</form></body></html>
EOF

