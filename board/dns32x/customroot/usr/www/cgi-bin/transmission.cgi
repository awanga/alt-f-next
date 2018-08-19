#!/bin/sh

. common.sh
check_cookie

write_header "Transmission Setup"

mktt trdir_tt "Folder where downloads will occur.<br>
Sub-folders InProgress and Finished will be created<br>
If you drop a torrent file in this folder, downloading will start."

mktt block_tt "Example site from where a file with a list of IPs to block will be downloaded.<br>
You must be confident on the site, the default value is not endorsed."

CONFF=/etc/transmission/transmission.conf

WATCH_DIR=$(sed -n '/watch-dir/s|.*".*":.*"\(.*\)".*|\1|p' $CONFF)
WATCH_DIR=$(httpd -e "$WATCH_DIR")

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

	<form name="transmissionf" action="transmission_proc.cgi" method="post">
	<table><tr>
	<td>Transmission folder</td>
		<td><input type=text size=32 id="watch_dir" name="WATCH_DIR" value="$WATCH_DIR" $(ttip trdir_tt)>
		<td><input type=button onclick="browse_dir_popup('watch_dir')" value="Browse"></td>
		</tr>
	</table>
	<p><input type=submit name="submit" value="Submit">
		$(back_button)
		<input type=submit name="webPage" value="WebPage"> 
	</form></body></html>
EOF
