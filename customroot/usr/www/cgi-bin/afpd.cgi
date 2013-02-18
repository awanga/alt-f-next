#!/bin/sh

. common.sh
check_cookie
write_header "Afpd Setup"

CONF_AFPD=/etc/netatalk/afpd.conf
CONF_AVOL=/etc/netatalk/AppleVolumes.default

mktt ttopts "Leave blank to use the default options set above"

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
	<form id=afpdf name=afpdf action=afpd_proc.cgi method="post">
	<fieldset>
	<legend><strong>Directories to export</strong></legend><br>
EOF

if ! test -f "$CONF_AVOL"; then
	touch "$CONF_AVOL"
fi

awk '/^:DEFAULT:/ {
		def_found = 1
		printf "Default options: <input type=text size=30 name=\"def_opts\" value=\"%s\"><br>\n", substr($0, index($0, $2))
	}
	/^~/ {
		user_chk = "checked"
	}
	END {
		if (! def_found)
			print "Default options: <input type=text size=30 name=\"def_opts\" value=\"options:upriv,usedots ea:ad\"><br>\n"
		printf "Export users home directory: <input type=checkbox %s name=\"user_en\" value=\"yes\"><br><br>\n", user_chk
	}' $CONF_AVOL

cat<<-EOF
	<table>
	<tr>
		<th>Directory</th>
		<th>Browse</th>
		<th>Share Name</th>
		<th>Options</th>
	</tr>
EOF

awk -v ttip="$(ttip ttopts)" '/(^\/|^"\/)/ {
	FS = "\t"
	opts = ""
	if (index($0, ":"))
		opts = substr($0, index($0, $3))
	spit(cnt, strip($1), strip($2), opts) 
	cnt++
	}
	END { for (i=cnt; i<cnt+3; i++)
			spit(i, "", "", "")
		printf "</table><input type=hidden name=afpd_cnt value=\"%d\">\n", i
	}
	function strip(var) {
		return gensub("\"", "", "g", var)
	}
	function spit(cnt, ldir, shname, opts) {
		printf "<tr><td><input type=text id=ldir_%d name=ldir_%d value=\"%s\"></td>\n", cnt, cnt, ldir
		printf "<td><input type=button  onclick=\"browse_dir_popup(%cldir_%d%c)\" value=Browse></td>\n", 047, cnt, 047
		printf "<td><input type=text size=8 name=shname_%d value=\"%s\"></td>\n", cnt, shname
		printf "<td><input type=text name=opts_%d value=\"%s\" %s></td></tr>\n", cnt, opts, ttip
}' $CONF_AVOL

cat<<EOF
	</fieldset><br>
	<input type=submit name=submit value="Submit">$(back_button)
	</form></body></html>
EOF

