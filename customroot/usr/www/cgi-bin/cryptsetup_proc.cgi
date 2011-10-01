#!/bin/sh

. common.sh

check_cookie
read_args

CONFF=/etc/misc.conf

if test -f $CONFF; then
	. $CONFF
fi

#debug

if test "$action" = "Format"; then
	if test -f $CRYPT_KEYFILE -a -b /dev/$devto; then
		res="$(cryptsetup -q luksFormat --key-file=$CRYPT_KEYFILE /dev/$devto 2>&1)"
		if test $? != 0; then
			msg "$res"
		fi
	else
		msg "Password file or device does not exist"
	fi

elif test "$action" = "Submit"; then
	sed -i '/^CRYPT_KEYFILE=/d' $CONFF >& /dev/null

	if test -n "$keyfile"; then
		echo "CRYPT_KEYFILE=$(httpd -d $keyfile)" >> $CONFF
	fi
fi

#enddebug
gotopage /cgi-bin/sys_services.cgi 
