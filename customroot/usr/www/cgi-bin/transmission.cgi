#!/bin/sh

. common.sh
check_cookie

write_header "Transmission Setup"

CONFF=/var/lib/transmission
JSON=settings.json

webhost=$(hostname -i | tr -d ' ')

if ! test -e "$CONFF/$JSON"; then
	cp /etc/transmission/settings.json "$CONFF/$JSON"
fi

eval $(awk '/"download-dir"/ { \
		gsub(",|\\\\", "", $2); printf "DOWNLOAD_DIR=%s;", $2} \
	/"watch-dir"/ { \
		gsub(",|\\\\", "", $2); printf "WATCH_DIR=%s;", $2} \
	/"incomplete-dir"/ { \
		gsub(",|\\\\", "", $2); printf "INCOMPLETE_DIR=%s;", $2} \
	/"rpc-enabled"/ { \
		gsub(",|\\\\", "", $2); printf "ENABLE_WEB=%s;", $2} \
	/"ratio-limit"/ { \
		gsub(",|\\\\", "", $2); printf "SEED_RATIO=%s;", $2} \
	/"ratio-limit-enabled"/ { \
		gsub(",|\\\\", "", $2); printf "SEED_RATIO_ENABLED=%s;", $2}' \
	"$CONFF/$JSON")

if test "$ENABLE_WEB" = "true"; then
	chkweb="checked"
fi

if test "$SEED_RATIO_ENABLED" = "true"; then
	chkratio="checked"
fi

webbutton="enabled"
rctransmission status >& /dev/null
if test $? != 0 -o "$ENABLE_WEB" = "false" ; then
	webbutton="disabled"
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
	function edisable(chk, but, st) {
		if (st == "disabled")
			return;
		if (document.getElementById(chk).checked == true)
			document.getElementById(but).disabled = false;
		else
			document.getElementById(but).disabled = true;
		}
	</script>

	<form name=transmission action=transmission_proc.cgi method="post" >
	<table><tr>
	<td>Finished directory</td>
		<td><input type=text size=32 id=down_dir name=DOWNLOAD_DIR value="$DOWNLOAD_DIR"></td>
		<td><input type=button onclick="browse_dir_popup('down_dir')" value=Browse></td>
		</tr>
	<td>In progress directory</td>
		<td><input type=text size=32 id=inc_dir name=INCOMPLETE_DIR value="$INCOMPLETE_DIR"></td>
		<td><input type=button onclick="browse_dir_popup('inc_dir')" value=Browse></td>
		</tr>
	<td>Torrents directory</td>
		<td><input type=text size=32 id=watch_dir name=WATCH_DIR value="$WATCH_DIR">
		<td><input type=button onclick="browse_dir_popup('watch_dir')" value=Browse></td>
		</tr>

	<tr><td>Stop seeding</td>
		<td><input type=checkbox id="seedcheck" $chkratio name="SEED_RATIO_ENABLED" value="true" onclick="edisable('seedcheck','seedentry')">
		&ensp;when download/upload ratio is</td>
		<td><input type=text id="seedentry" size=3 name=SEED_RATIO value="$SEED_RATIO"></td>
		</tr>

	<tr><td>Enable web page</td><td><input type=checkbox id="webcheck" $chkweb name="ENABLE_WEB" value="true" onclick="edisable('webcheck','webbut', '$webbutton')"></td></tr>
	<tr><td></td><td><input type=submit value=Submit>
		$(back_button)
		<input type="button" id="webbut" $webbutton value="WebPage" onClick="document.location.href='http://$webhost:9091';">
	</td></tr>
	</table></form></body></html>
EOF
