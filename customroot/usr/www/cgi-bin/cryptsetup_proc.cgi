#!/bin/sh

. common.sh

check_cookie
read_args

CONFF=/etc/misc.conf

if test -f $CONFF; then
	. $CONFF
fi

#debug

sed -i '/^CRYPT_KEYFILE=/d' $CONFF >& /dev/null

if test -n "$keyfile"; then
	echo "CRYPT_KEYFILE=$(httpd -d $keyfile)" >> $CONFF
fi

#enddebug
gotopage /cgi-bin/sys_services.cgi 
