#!/bin/sh

. common.sh

check_cookie
read_args

#debug

CONFF=/etc/httpd.conf

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
A:192.168.1.0/255.255.255.0 #!# Allow local net
EOF

cat $TF >> $CONFF
rm $TF

#enddebug
gotopage /cgi-bin/inetd.cgi 
