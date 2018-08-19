
eval $(awk '{ if ($6 == "/usr/sbin/sshd") {
		if ($1 == "ssh_alt" || $1 == "#ssh_alt")
			print "SSHD_2222=checked; osshd_port=2222";
		else
			print "SSHD_22=checked; osshd_port=22";
		if (index($1,"#")) print "sshd_server=checked;"; else print "sshd_inetd=checked;";
	}
}' $CONF_INETD)

cat<<-EOF
	<fieldset><legend>OpenSSH sshd</legend>
	<table>
	<tr><td>Listen on port</td>
	<td>22<input type=radio name=sshd_port id="sshd_22" $SSHD_22 value="22" onclick="toogle(this)">
	2222<input type=radio name=sshd_port id="sshd_2222" $SSHD_2222 value="2222" onclick="toogle(this)"></td></tr>
	<tr><td></td><td></td></tr>
	<tr><td>inetd mode</td><td><input type=radio $sshd_inetd name=sshd_server value="no" $(ttip inetd_tt)></td></tr>
	<tr><td>server mode</td><td><input type=radio $sshd_server name=sshd_server value="yes" $(ttip server_tt)></td></tr>
	</table>
	<input type="hidden" name=osshd_port value="$osshd_port">
	</fieldset>
EOF
