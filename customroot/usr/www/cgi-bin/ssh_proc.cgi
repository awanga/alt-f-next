#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_INETD=/etc/inetd.conf
CONF_DB=/etc/init.d/S62dropbear

opts=""

if test -n "$db_nopass"; then
	opts="$opts -s"
fi

if test -n "$db_noroot"; then
	opts="$opts -w"
fi

if test -n "$db_norootpass"; then
	opts="$opts -g"
fi

srv="ssh_alt"
if test "$db_port" = 22; then
	srv="ssh"
fi

#osrv="ssh_alt"
#if test "$odb_port" = 22; then
#	osrv="ssh"
#fi

sed -i "/\/usr\/sbin\/dropbear/s|^.*\(stream.*dropbear -i\).*\(#.*$\)|#${srv}\t\1${opts}\t\2|" $CONF_INETD
sed -i "s/OPTS=.*/OPTS=\"$opts -p $db_port\"/" $CONF_DB

rcinetd disable ssh ssh_alt >& /dev/null

if test "$db_server" = "yes"; then
	#rcinetd disable $osrv $srv >& /dev/null
	rcdropbear enable >& /dev/null
	rcdropbear restart >& /dev/null
else
	rcdropbear disable >& /dev/null
	rcdropbear stop >& /dev/null
	rcinetd enable $srv >& /dev/null
fi

if test -f sshd_proc.cgi; then
	. sshd_proc.cgi
fi

#enddebug
gotoback $from_url ssh.cgi

