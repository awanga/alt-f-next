#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/ushare.conf

for i in $(seq 1 $cnt); do
	d="$(eval echo \$sdir_$i)"
	if test -n "$d"; then
		res="$d,$res"
	fi
done

shares="$(httpd -d $res)"

if test -z "$ENABLE_WEB"; then ENABLE_WEB="no"; fi

sed -i 's|USHARE_DIR=.*$|USHARE_DIR='"$shares"'|' $CONFF
sed -i 's|ENABLE_WEB=.*$|ENABLE_WEB='"$ENABLE_WEB"'|' $CONFF

rcushare status >& /dev/null
if test $? = 0; then
	rcushare reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

