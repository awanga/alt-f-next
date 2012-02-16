#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_INETD=/etc/inetd.conf

opts="-i"

if test -n "$nopass"; then
	opts="$opts -s"
fi

if test -n "$noroot"; then
	opts="$opts -w"
fi

if test -n "$norootpass"; then
	opts="$opts -g"
fi

sed -i '/\(^ssh\|#ssh\)/s/-i.*$/'"$opts"'/' $CONF_INETD

rcinetd	reload >& /dev/null

#enddebug
gotopage /cgi-bin/inetd.cgi

