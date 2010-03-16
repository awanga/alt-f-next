#!/bin/sh

. common.sh
check_cookie

write_header "Transmission Setup"

CONFF=/etc/transmission.conf

. $CONFF

if test -n "$CONF_DIR" -a -f "$CONF_DIR/settings.json"; then
	eval $(awk '/"download-dir"/{sub(",", "", $2); printf "DOWNLOAD_DIR=%s;", $2} \
		/"watch-dir"/{sub(",", "", $2); printf "WATCH_DIR=%s", $2}' \
		"$CONF_DIR/settings.json")
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
	</script>

	<form name=transmission action=transmission_proc.cgi method="post" >
	<table><tr>
	<td>Configuration directory</td>
		<td><input type=text size=20 id=conf_dir name=CONF_DIR value=$CONF_DIR></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir')" value=Browse></td>
		</tr>
	<td>Download directory</td>
		<td><input type=text size=20 id=down_dir name=DOWNLOAD_DIR value=$DOWNLOAD_DIR></td>
		<td><input type=button onclick="browse_dir_popup('down_dir')" value=Browse></td>
		</tr>
	<td>Watch directory</td>
		<td><input type=text size=20 id=watch_dir name=WATCH_DIR value=$WATCH_DIR>
		<td><input type=button onclick="browse_dir_popup('watch_dir')" value=Browse></td>
		</tr>
	<tr><td><input type=submit value=Submit></td>
	</table></form></body></html>
EOF
