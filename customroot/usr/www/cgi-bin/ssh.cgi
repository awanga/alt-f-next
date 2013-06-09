#!/bin/sh

. common.sh
check_cookie
write_header "SSH Server Setup"

#debug

CONF_INETD=/etc/inetd.conf

eval $(awk '{ if ($6 == "/usr/sbin/dropbear") {
		if ( $1 == "ssh" || $1 == "#ssh") print "DB_22=checked; ";
		if ( $1 == "ssh_alt" || $1 == "#ssh_alt") print "DB_2222=checked; ";
		if (index($0,"-s")) print "DB_NOPASS_CHK=checked; "
		if (index($0,"-w")) print "DB_NOROOT_CHK=checked; "
		if (index($0,"-g")) print "DB_NOROOTPASS_CHK=checked; "
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
	<fieldset><legend>Configure Dropbear</legend>
	<table>
	<tr><td>Disable password logins</td><td><input type=checkbox $DB_NOPASS_CHK name=db_nopass value=yes></td></tr>
	<tr><td>Disallow root logins</td><td><input type=checkbox $DB_NOROOT_CHK name=db_noroot value=yes></td></tr>
	<tr><td>Disable password logins for root</td><td><input type=checkbox $DB_NOROOTPASS_CHK name=db_norootpass value=yes></td></tr>
	<tr><td>Listen on port</td>
	<td>22<input type=radio $DB_22 id="db_22" name=db_port value="22" onclick="toogle(this)">
	2222<input type=radio $DB_2222 id="db_2222" name=db_port value="2222" onclick="toogle(this)"></td>
	</table>
	</fieldset>
EOF

if test -f sshd.cgi; then
	. sshd.cgi
fi

cat<<-EOF
	<input type="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
