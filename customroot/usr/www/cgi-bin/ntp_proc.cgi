#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/ntp.conf

#debug

sed -i '/^server/d' $CONFF
echo "server 127.127.1.0" >> $CONFF

sed -i '/^NTPD_/d' $CONFF

for i in $(seq 1 3); do
	if test -n "$(eval echo \$server_$i)"; then
		echo "server $(eval echo \$server_$i)" >> $CONFF
	fi
done

echo "NTPD_DAEMON=$runasdaemon" >> $CONFF
if test -z "$runatboot"; then
	runatboot=no
fi
echo "NTPD_BOOT=$runatboot" >> $CONFF

rcntp status >/dev/null 2>&1
if test $? = 0; then
	rcntp restart >/dev/null 2>&1
fi

#enddebug
gotopage /cgi-bin/net_services.cgi

