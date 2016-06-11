#!/bin/sh

. common.sh
check_cookie
read_args

write_header "forked-daapd Setup"

mktt sname_tt "Advertised name.<br>A '%h' will be replaced with the host name."
CONF_FORKED=/etc/forked-daapd.conf

SHARE_DIRS=$(sed -n '
\|^[^#]*directories|{
s|.*directories.*=.*{\(.*\)}|\1|
s|" *, *"|\n|g
s|\\"|"|g
s|\\,|,|g
s|"\(.*\)"|\1|gp
}' $CONF_FORKED)

SNAME=$(sed -n 's/\tname = "\(.*\)"/\1/p' $CONF_FORKED)

cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
			start_dir = document.getElementById(input_id).value;
			if (start_dir == "")
				start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
	</script>

	<form name=forked action=forked_daapd_proc.cgi method="post" >
	<table>
		<tr><th>Share Folder</th><th></th></tr>
EOF

k=1
for i in $SHARE_DIRS; do
	cat<<-EOF
		<td><input type=text size=32 id="sdir_$k" name="sdir_$k" value=$(httpd -e "$i")></td>
		<td><input type=button onclick="browse_dir_popup('sdir_$k')" value=Browse></td>
		</tr>
	EOF
    k=$((k+1))
done

for j in $(seq $k $((k+2))); do
	cat<<-EOF
		<td><input type=text size=32 id="conf_dir_$j" name="sdir_$j" value=""></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$j')" value=Browse></td>
		</tr>
	EOF
done

cat<<-EOF
	</table><br><table>
	<tr><td>Server Name</td><td><input type=text name=sname value="$SNAME" $(ttip sname_tt)></td></tr>
	</table>
	<input type=hidden name="cnt" value="$j">
	<p><input type=submit value=Submit>$(back_button)
	</form></body></html>
EOF
