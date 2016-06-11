#!/bin/sh

. common.sh
check_cookie
read_args

CONFN=/etc/ntp.conf
CONFF=/etc/misc.conf

#debug

sed -i '/^server/d' $CONFN
echo "server 127.127.1.0" >> $CONFN

sed -i '/^NTPD_/d' $CONFF >& /dev/null

for i in $(seq 1 3); do
	if test -n "$(eval echo \$server_$i)"; then
		echo "server $(eval echo \$server_$i)" >> $CONFN
	fi
done

if test "$runasdaemon" = "no"; then
	runasdaemon=$croni
fi

echo "NTPD_DAEMON=$runasdaemon" >> $CONFF
if test -z "$runatboot"; then
	runatboot=no
fi
echo "NTPD_BOOT=$runatboot" >> $CONFF

if rcntp status >& /dev/null ; then
	rcntp restart >& /dev/null
fi

#enddebug
gotopage /cgi-bin/net_services.cgi

