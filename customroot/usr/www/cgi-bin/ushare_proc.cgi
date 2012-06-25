#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_USHARE=/etc/ushare.conf

if test -n "$webPage"; then
	USHARE_DIR="$(awk -F= '/^USHARE_DIR/{print $2}' $CONF_USHARE)" 
	eval $(grep ^USHARE_PORT $CONF_USHARE)
	webhost="${HTTP_HOST%%:*}:$USHARE_PORT/web/ushare.html"
	embed_page "http://$webhost" "uShare Page"
fi

for i in $(seq 1 $cnt); do
	d="$(eval echo \$sdir_$i)"
	if test -z "$d"; then continue; fi
	if ! test -d "$(httpd -d $d)"; then
		msg "At least one directory does not exists."
	fi
	res="$d,$res"
done

if test -n "$res"; then shares="$(httpd -d $res)"; fi

if test -z "$ENABLE_WEB"; then ENABLE_WEB="no"; fi

sed -i 's|USHARE_DIR=.*$|USHARE_DIR='"$shares"'|' $CONF_USHARE
sed -i 's|ENABLE_WEB=.*$|ENABLE_WEB='"$ENABLE_WEB"'|' $CONF_USHARE
sed -i 's|USHARE_NAME=.*$|USHARE_NAME='"$(httpd -d $sname)"'|' $CONF_USHARE

if rcushare status >& /dev/null; then
	rcushare reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

