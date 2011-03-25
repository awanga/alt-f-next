#!/bin/sh

. common.sh
check_cookie

write_header "Transmission Setup"

mktt trdir_tt "Directory where downloads will occur.<br>
Subdirectories InProgress and Finished will be created<br>
If you drop a torrent file in this directory, downloading will start."

mktt block_tt "Example site from where a file with a list of IPs to block will be downloaded.<br>
You must be confident on the site, the default value is not endorsed."

CONFF=/var/lib/transmission
JSON=settings.json

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
		gsub(",|\\\\", "", $2); printf "SEED_RATIO_ENABLED=%s;", $2} \
	/"blocklist-enabled"/ { \
		gsub(",|\\\\", "", $2); printf "BLOCKLIST_ENABLED=%s;", $2} \
	/"blocklist-url"/ { \
		gsub(",|\\\\", "", $2); printf "BLOCKLIST_URL=%s;", $2} \
	/"idle-seeding-limit-enabled"/ { \
		gsub(",|\\\\", "", $2); printf "SEED_LIMIT_ENABLED=%s;", $2} \
	/"idle-seeding-limit"/ { \
		gsub(",|\\\\", "", $2); printf "SEED_LIMIT=%s;", $2}' \
	"$CONFF/$JSON")

if test "$ENABLE_WEB" = "true"; then
	chkweb="checked"
fi

if test "$SEED_RATIO_ENABLED" = "true"; then
	chkratio="checked"
fi

if test "$SEED_LIMIT_ENABLED" = "true"; then
	chklimit="checked"
fi

if test "$BLOCKLIST_ENABLED" = "true"; then
	chkblock="checked"
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
	<td>Transmission directory</td>
		<td><input type=text size=32 id=watch_dir name=WATCH_DIR value="$WATCH_DIR" $(ttip trdir_tt)>
		<td><input type=button onclick="browse_dir_popup('watch_dir')" value=Browse></td>
		</tr>

	<tr><td>Stop seeding</td>
		<td><input type=checkbox id="seedcheck" $chkratio name="SEED_RATIO_ENABLED" value="true" onclick="edisable('seedcheck','seedentry')">
		&ensp;when upload/download ratio is</td>
		<td><input type=text id="seedentry" size=3 name=SEED_RATIO value="$SEED_RATIO"></td>
		</tr>

	<tr><td>Stop seeding</td>
		<td><input type=checkbox id="limitcheck" $chklimit name="SEED_LIMIT_ENABLED" value="true" onclick="edisable('limitcheck','limitentry')">
		&ensp;after downloading completes</td>
		<td><input type=text id="limitentry" size=3 name=SEED_LIMIT value="$SEED_LIMIT">&ensp;min</td>
		</tr>

	<tr><td>Enable blocklist</td>
		<td><input type=checkbox id="blockcheck" $chkblock name="BLOCKLIST_ENABLED" value="true" onclick="edisable('blockcheck','blockentry')">
		&ensp;blocklist download url</td>
		<td><input type=text id="blockentry" size=30 name=BLOCKLIST_URL value="$BLOCKLIST_URL" $(ttip block_tt)></td>
		</tr>

	<tr><td>Enable web page</td><td><input type=checkbox id="webcheck" $chkweb name="ENABLE_WEB" value="true" onclick="edisable('webcheck','webbut', '$webbutton')"></td></tr>
	<tr><td></td><td><input type=submit value=Submit>
		$(back_button)
		<input type="submit" id="webbut" $webbutton name=webPage value="WebPage"> 
	</td></tr>
	</table></form></body></html>
EOF
