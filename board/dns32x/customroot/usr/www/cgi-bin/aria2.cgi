#!/bin/sh

. common.sh
check_cookie

write_header "Aria2 Setup"

mktt trdir_tt "Folder where downloads will occur."

CONFF=/etc/aria2/aria2.conf

DL_DIR=$(awk -F= '/^dir=/{print $2}' $CONFF)
DL_DIR=$(httpd -e "$DL_DIR")

if ! ipkg status aria2web | grep -q '^Status.*installed'; then
	web_dis=disabled
elif ! rcaria2 status >& /dev/null; then
	web_dis=disabled
elif ! rclighttpd status >& /dev/null; then
	web_dis=disabled
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

	<form name="aria2f" action="aria2_proc.cgi" method="post">
	<table><tr>
	<td>Aria2 folder</td>
		<td><input type=text size=32 id="dl_dir" name="DL_DIR" value="$DL_DIR" $(ttip trdir_tt)>
		<td><input type=button onclick="browse_dir_popup('dl_dir')" value="Browse"></td>
		</tr>
	</table>
	<p><input type=submit name="submit" value="Submit">
		$(back_button)
		<input type=submit $web_dis name="webPage" value="WebPage"> 
	</form></body></html>
EOF
