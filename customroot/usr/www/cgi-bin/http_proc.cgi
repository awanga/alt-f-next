#!/bin/sh

. common.sh

check_cookie
read_args

#debug

CONFF=/etc/httpd.conf
INETD_CONF=/etc/inetd.conf
STUNNEL_CONF=/etc/stunnel/stunnel.conf
CONFS=/etc/init.d/S41stunnel

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK

TF=$(mktemp)

for i in $(seq 1 $httpd_cnt); do

	remip=$(eval echo \$remip_$i)

	if test -n "$remip"; then

		remip=$(httpd -d $remip)
		nip=$(echo $remip | cut -d/ -f1)
		nnetwork=$(echo $remip | cut -d/ -f2)

		if test "$nnetwork" = "$NETWORK"; then
			msg "All hosts from the local network are already\n\
allowed to access the administrative web pages.\n\n\
Specify, if needed, an external IP address that\n\
you wish to also have access to the administrative web pages.\n"
		fi

		if ! checkip $nip; then
			msg "The IP must be in the form x.x.x.x, where x is from 1 to 3 digits, or x.x.x.x/y.y.y.y, or x.x.x.x/n"
		fi

		dis=""
		if test -n "$(eval echo \$dis_$i)"; then dis="#"; fi

		echo "${dis}A:$remip #!# Allow remote" >> $TF
	fi
done

cat<<EOF > $CONFF
A:127.0.0.1     #!# Allow local loopback connections
D:*             #!# Deny from other IP connections
A:$NETWORK/$netmask #!# Allow local net
EOF

cat $TF >> $CONFF
rm $TF

if false; then
	if grep -q 'server.port.*=.*8080' /etc/lighttpd/lighttpd.conf; then echo yes; fi
	grep '^include.*ssl.conf' /etc/lighttpd/lighttpd.conf

	port=$(grep ^server.port $CONF_LIGHTY | cut -d" " -f3)
	sslport=$(sed -n 's/$SERVER\["socket"\] == ":\(.*\)".*/\1/p' $CONF_SSL)
fi

case $port in
	8080) sed -i 's/http[\t ]/http_alt\t/' $INETD_CONF ;;
	80) sed -i 's/http_alt/http/' $INETD_CONF ;;
esac

case $sport in
	8443) sed -i 's/https[\t ]/https_alt\t/' $INETD_CONF ;;
	443) sed -i 's/https_alt/https/' $INETD_CONF ;;
esac

if test "$stunnel" = "server"; then
	rcinetd disable https https_alt swats >& /dev/null
	if test "$sport" = "8443"; then
		sed -i 's/^accept.*=.*443/accept = 8443/' $STUNNEL_CONF
	else
		sed -i 's/^accept.*=.*443/accept = 443/' $STUNNEL_CONF
	fi
	sed -i 's/^#TYPE=/TYPE=/' $CONFS
	rcstunnel restart >& /dev/null
	rcstunnel enable >& /dev/null
else
	sed -i 's/^TYPE=/#TYPE=/' $CONFS
	rcstunnel stop >& /dev/null
	rcstunnel disable >& /dev/null
	if test "$sport" = "8443"; then
		rcinetd enable swats https_alt >& /dev/null
	else
		rcinetd enable swats https >& /dev/null
	fi
fi

#enddebug
gotopage /cgi-bin/inetd.cgi 
