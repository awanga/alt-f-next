#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_INETD=/etc/inetd.conf

opts="-i"

if test -n "$db_nopass"; then
	opts="$opts -s"
fi

if test -n "$db_noroot"; then
	opts="$opts -w"
fi

if test -n "$db_norootpass"; then
	opts="$opts -g"
fi

cmt=""
if grep -q '^#.*\/usr\/sbin\/dropbear' $CONF_INETD; then
	cmt="#"
fi

db_inetd="\tstream\ttcp\tnowait\troot\t/usr/sbin/dropbear\tdropbear "

if test "$db_port" = 22; then
	sed -i "/\/usr\/sbin\/dropbear/s|^.*$|${cmt}ssh${db_inetd}${opts}|" $CONF_INETD
elif test "$db_port" = 2222; then
	sed -i "/\/usr\/sbin\/dropbear/s|^.*$|${cmt}ssh_alt${db_inetd}${opts}|" $CONF_INETD
fi

if test -f sshd_proc.cgi; then
	. sshd_proc.cgi
fi

rcinetd reload >& /dev/null

#enddebug
gotopage /cgi-bin/inetd.cgi

