#!/bin/sh

. common.sh
check_cookie
read_args

write_header "SABnzbd Setup"

CONFF=/etc/sabnzbd/sabnzbd.conf
SABNZBD_SITE=http://sourceforge.net/projects/sabnzbdplus/files/sabnzbdplus
SABNZBD_DIR=/opt/SABnzbd

mktt tt_update "Fill in the SABnzbd version to update to, e.g. <tt>0.7.6</tt> and hit the Update Button.<br>
New versions are announced at the top left of the SABnzbd main page."

maindir=$(sed -n 's|^dirscan_dir *= *\(.*\)|\1|p' $CONFF)

curver=$(sed -n 's/^Version: \(.*\)/\1/p' $SABNZBD_DIR/PKG-INFO)

# too slow...
if false; then
	tfile=$(mktemp)

	if ! wget -q --tries=1 --timeout=3 -O $tfile $SABNZBD_SITE ; then
		update_dis="disabled"
		lastver="download site unavailable"
	else
		lastver=$(sed -n 's/.*Click to enter \(.\..\..\)"/\1/p' $tfile| head -n1)
		if test -z "$lastver"; then
			update_dis="disabled"
			lastver="unable to retrieve last version"
		elif test "$lastver" = "$curver"; then
			update_dis="disabled"
			lastver="is up to date"
		fi
	fi

	rm -f $tfile
else
	lastver="$curver"
fi

if ! rcsabnzbd status >& /dev/null; then
	webbut_dis=disabled
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

	<form name=sabnzbd action=sabnzbd_proc.cgi method="post" >
	<table>
	<tr><td>SABnzbd Folder</td>
	<td><input type=text size=32 id="conf_dir" name="conf_dir" value="$(httpd -e "$maindir")"></td>
	<td><input type=button onclick="browse_dir_popup('conf_dir')" value=Browse></td>
	</tr>
	<tr><td>Update to version</td><td><input type=text name=version value="$lastver" $(ttip tt_update)>(current is $curver)</td>
	<td><input type=submit $update_dis name=update value=Update></td></tr></table>
	
	<input type=hidden name=curver value="$curver">
	<p><input type=submit name=submit value=Submit> $(back_button)
	<input type="submit" $webbut_dis name=webPage value=WebPage>
	</form></body></html>
EOF
