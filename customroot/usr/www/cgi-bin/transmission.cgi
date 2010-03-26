#!/bin/sh

. common.sh
check_cookie

write_header "Transmission Setup"

CONFF=/etc/transmission.conf
OJSON=/etc/transmission/settings.json

webhost=$(hostname -i | tr -d ' ')

rctransmission status >& /dev/null
if test $? != 0; then
		webchk="disabled"
fi

if test -e $CONFF; then # damned spaced in file names!
	CONF_DIR="$(awk -F= '/^CONF_DIR/{print $2}' $CONFF)" 
	DOWNLOAD_DIR="$(awk -F= '/^DOWNLOAD_DIR/{print $2}' $CONFF)" 
	WATCH_DIR="$(awk -F= '/^WATCH_DIR/{print $2}' $CONFF)" 
fi

if test -n "$CONF_DIR"; then
	JSON="$CONF_DIR/settings.json";
	if test -f "$JSON"; then
		if test "$CONFF" -ot "$JSON"; then
			eval $(awk '/"download-dir"/{gsub(",|\\\\", "", $2); \
				printf "DOWNLOAD_DIR=%s;", $2} \
				/"watch-dir"/{gsub(",|\\\\", "", $2); \
				printf "WATCH_DIR=%s", $2}' \
				"$JSON")
		fi
	else
		mkdir -p "$CONF_DIR"
		cp $OJSON $JSON 
		sed -i -e 's|.*"download-dir":.*|    "download-dir": "'$DOWNLOAD_DIR'",|' \
		  -e 's|.*"watch-dir":.*|    "watch-dir": "'$WATCH_DIR'",|' "$JSON"
	fi
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
		<td><input type=text size=32 id=conf_dir name=CONF_DIR value="$CONF_DIR"></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir')" value=Browse></td>
		</tr>
	<td>Download directory</td>
		<td><input type=text size=32 id=down_dir name=DOWNLOAD_DIR value="$DOWNLOAD_DIR"></td>
		<td><input type=button onclick="browse_dir_popup('down_dir')" value=Browse></td>
		</tr>
	<td>Watch directory</td>
		<td><input type=text size=32 id=watch_dir name=WATCH_DIR value="$WATCH_DIR">
		<td><input type=button onclick="browse_dir_popup('watch_dir')" value=Browse></td>
		</tr>
	<tr><td></td><td><input type=submit value=Submit>
		$(back_button)
		<input type="button" $webchk value="WebPage" onClick="document.location.href='http://$webhost:9091';">
	</td></tr>
	</table></form></body></html>
EOF
