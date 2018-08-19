
CONF2_SSHD=/etc/ssh/sshd_config

srv="ssh_alt"
if test "$sshd_port" = 22; then
	srv="ssh"
fi

opt1=yes
if test -n "$db_nopass"; then
	opt1=no
fi

if test -n "$db_noroot"; then
	if test -n "$db_norootpass"; then
		opt2=without-password
	else
		opt2=no
	fi
else
	opt2=yes
fi

sed -i "/\/usr\/sbin\/sshd/s|.*\(stream.*\)|#${srv}\t\1|" $CONF_INETD

sed -i -e 's/^[# ]*PermitRootLogin.*/PermitRootLogin '$opt1'/' \
	-e 's/^[# ]*PasswordAuthentication.*/PasswordAuthentication '$opt2'/' \
	-e 's/^[# ]*Port.*/Port '$sshd_port'/' \
	$CONF2_SSHD

# inetd ssh ssh_alt already disabled in ssh_proc

if test "$sshd_server" = "yes"; then
	#rcinetd disable $osrv $srv >& /dev/null
	rcopensshd enable >& /dev/null
	rcopensshd restart >& /dev/null
else
	rcopensshd disable >& /dev/null
	rcopensshd stop >& /dev/null
	rcinetd enable $srv >& /dev/null
fi
