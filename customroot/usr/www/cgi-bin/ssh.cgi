#!/bin/sh

. common.sh
check_cookie
write_header "SSH Servers Setup"

#debug

CONF_INETD=/etc/inetd.conf

mktt inetd_tt "Inetd mode: runs only when necessary, slower to start, conserves memory."
mktt server_tt "Server mode: always running, faster, always consuming memory<br>
(the ssh/dropbear checkboxes in the inetd web page will be unchecked)."

eval $(awk '{ if ($6 == "/usr/sbin/dropbear") {
		if ($1 == "ssh_alt" || $1 == "#ssh_alt")
			print "DB_2222=checked; odb_port=2222"; 
		else
			print "DB_22=checked; odb_port=22";
		if (index($1,"#")) print "db_server=checked;"; else print "db_inetd=checked;";
		if (index($0,"-s")) print "DB_NOPASS_CHK=checked;"
		if (index($0,"-w")) print "DB_NOROOT_CHK=checked;"
		if (index($0,"-g")) print "DB_NOROOTPASS_CHK=checked;"
	}
}' $CONF_INETD)

cat<<-EOF
	<script type="text/javascript">
	function toogle(obj) {
		curr = obj.value
		if (curr == "22")
			other = "2222"
		else
			other = "22"

		if (obj.name == "db_port") {
			document.getElementById("sshd_" + curr).checked = false;
			document.getElementById("sshd_" + other).checked = true;
		} else {
			document.getElementById("db_" + curr).checked = false;
			document.getElementById("db_" + other).checked = true;
		}
	}
	</script>
	<form name="ssh" action="/cgi-bin/ssh_proc.cgi" method="post">
	<fieldset><legend>Dropbear</legend>
	<table>
	<tr><td>Listen on port</td>
	<td>22<input type=radio $DB_22 id="db_22" name=db_port value="22" onclick="toogle(this)">
	2222<input type=radio $DB_2222 id="db_2222" name=db_port value="2222" onclick="toogle(this)"></td></tr>
	<tr><td></td><td></td></tr>
	<tr><td>inetd mode</td><td><input type=radio $db_inetd name=db_server value="no" $(ttip inetd_tt)></td></tr>
	<tr><td>server mode</td><td><input type=radio $db_server name=db_server value="yes" $(ttip server_tt)></td></tr>
	</table>
	<input type="hidden" name=odb_port value="$odb_port">
	</fieldset>
EOF

if test -f sshd.cgi; then
	. sshd.cgi
fi

cat<<-EOF
	<table>
	<tr><td>Disable password logins</td><td><input type=checkbox $DB_NOPASS_CHK name=db_nopass value=yes></td></tr>
	<tr><td>Disallow root logins</td><td><input type=checkbox $DB_NOROOT_CHK name=db_noroot value=yes></td></tr>
	<tr><td>Disable password logins for root</td><td><input type=checkbox $DB_NOROOTPASS_CHK name=db_norootpass value=yes></td></tr>
	<tr><td></td><td></td></tr>
	</table>
	<input type="hidden" name=from_url value="$HTTP_REFERER">
	<input type="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
