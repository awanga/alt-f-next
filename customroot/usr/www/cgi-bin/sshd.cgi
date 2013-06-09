
eval $(awk '{ if ($6 == "/usr/sbin/sshd") {
		if ( $1 == "ssh" || $1 == "#ssh") print "SSHD_22=checked; ";
		if ( $1 == "ssh_alt" || $1 == "#ssh_alt") print "SSHD_2222=checked; ";
	}
}' $CONF_INETD)

cat<<-EOF
	<fieldset><legend>Configure OpenSSH sshd</legend>
	<table>
	<tr><td>Listen on port</td>
	<td>22<input type=radio name=sshd_port id="sshd_22" $SSHD_22 value="22" onclick="toogle(this)">
	2222<input type=radio name=sshd_port id="sshd_2222" $SSHD_2222 value="2222" onclick="toogle(this)"></td>
	</tr></table>
	</fieldset>
EOF
