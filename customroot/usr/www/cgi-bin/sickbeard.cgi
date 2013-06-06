#!/bin/sh

. common.sh
check_cookie
read_args

write_header "SickBeard Setup"

SBCONF=/etc/sickbeard/sickbeard.conf
SABPROG=/opt/SABnzbd/SABnzbd.py
NZBGETPROG=/usr/bin/nzbget

if ! test -x $SABPROG; then sab_dis=disabled; fi
if ! test -x $NZBGETPROG; then nzbget_dis=disabled; fi
if test -n "$sab_dis" -a -n "$nzbget_dis"; then dlmsg="(none installed)"; fi

dlnd=$(sed -n 's/nzb_method.*=[[:space:]]*\(.*\)/\1/p' $SBCONF)
if test "$dlnd" = "sabnzbd"; then sab_chk=checked; fi
if test "$dlnd" = "nzbget"; then nzbget_chk=checked; fi

maindir=$(sed -n 's/^root_dirs.*=.*|\(.*\)/\1/p' $SBCONF)

if ! rcsickbeard status >& /dev/null; then
	webbut_dis="disabled"
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

	<form name=sickbeardf action=sickbeard_proc.cgi method="post" >
	<table>
	<tr><td>SickBeard Folder</td>
	<td><input type=text size=32 id="conf_dir" name="conf_dir" value="$(httpd -e "$maindir")"></td>
	<td><input type=button onclick="browse_dir_popup('conf_dir')" value=Browse></td>
	</tr>
	<tr><td>Downloaders:</td><td>
	SABnzbd<input type=radio $sab_dis $sab_chk name=downld value="sabnzbd">
	NZBget<input type=radio $nzbget_dis $nzbget_chk name=downld value="nzbget">
	$dlmsg</td><td></td></tr>
	</table>
	<p><input type=submit name=submit value=Submit> $(back_button)
	<input type="submit" $webbut_dis name=webPage value=WebPage>
	</form></body></html>
EOF
