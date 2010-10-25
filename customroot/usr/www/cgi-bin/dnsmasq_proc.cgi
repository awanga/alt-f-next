#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_H=/etc/dnsmasq-hosts
CONF_O=/etc/dnsmasq-opts
CONF_F=/etc/dnsmasq.conf
CONF_NTP=/etc/ntp.conf

if test -n "$Submit"; then
	if test -z "$high_rg" -o -z "$low_rg" -o -z "$lease"; then
		msg "Ip start, IP end and Lease all must be specified"
	elif ! $(checkip $high_rg); then
		msg "The start IP must be in the form x.x.x.x, where x is greater than 0 and lower then 255."
	elif ! $(checkip $low_rg); then
		msg "The end IP must be in the form x.x.x.x, where x x is greater than 0 and lower then 255."
	elif ! $(echo $lease | grep -q -e '^[0-9]\{1,3\}[mh]\?$'); then
		msg "Lease time must be an integer specifying seconds, minutes (20m), or hours (3h)"
	fi

	sed -i '/^dhcp-range=/d' $CONF_F
	echo "dhcp-range=$low_rg,$high_rg,$lease" >> $CONF_F

	net=$(hostname -d)
	sed -i '/^domain=/d' $CONF_F
	echo "domain=$net" >> $CONF_F

	gw=$(route -n | awk '/^0.0.0.0/{print $2}')
	sed -i '/^option:router,/d' $CONF_O
	echo "option:router,$gw	# default route" >> $CONF_O

	sed -i '/^option:ntp-server/d' $CONF_O
	if test "$ntp" = "local"; then
		echo "option:ntp-server,0.0.0.0	# ntp server" >> $CONF_O
	elif test "$ntp" = "server"; then
			if test -z "$ntp_entry"; then continue; fi
			res="$(nslookup $ntp_entry 2> /dev/null)"
			if test $? != 0; then
				msg "Can't get $ntp_entry IP."
			fi
			ntph=$(echo "$res" | awk '/Address/{ if (NR == 5) print $3}')
			echo "option:ntp-server,$ntph	# ntp server" >> $CONF_O
	fi

	echo > $CONF_H
	for i in $(seq 0 $cnt_din); do
		nm=$(eval echo \$nm_$i)
		ip=$(eval echo \$ip_$i)
		mac=$(httpd -d "$(eval echo \$mac_$i)")
		lease=$(eval echo \$lease_$i)

		if test -z "$nm" -a -z "$ip" -a -z "$mac"; then continue; fi

		if test -z "$nm" -o -z "$ip" -o -z "$mac"; then
			msg "You must specify a name, IP and MAC"
		fi
		
		if ! $(checkname $nm); then
			msg "The host name can only have letters and digits, no spaces, and must begin with a letter"
		elif ! $(checkip $ip); then
			msg "The IP must be in the form x.x.x.x, where x is greater than 0 and lower then 255."
		elif ! $(checkmac $mac); then
			msg "The MAC must be in the form xx:xx:xx:xx:xx:xx, where x is one digit or one letter in the 'a' to 'f' range"
		elif test -n "$lease"; then
			if ! $(echo "$lease" | grep -q -e '^[0-9]\{1,3\}[mh]\?$'); then
				msg "Lease time must be an integer specifying seconds, minutes (20m), or hours (3h)"
			fi
		fi

		if test -z "$lease"; then
			echo "$mac,$nm,$ip" >> $CONF_H
		else
			echo "$mac,$nm,$ip,$lease" >> $CONF_H
		fi
	done
	
	sed -i '/enable-tftp/d' $CONF_F
	if test -n "$tftp"; then
		echo "enable-tftp" >> $CONF_F
		sed -i '/^option:tftp-server,/d' $CONF_O
		echo "option:tftp-server,0.0.0.0	# boot server" >> $CONF_O
	fi

	if test -n "$tftproot"; then
		sed -i '/tftp-root/d' $CONF_F
		echo "tftp-root=\"$(httpd -d $tftproot)\"" >> $CONF_F
	fi

	sed -i '/log-queries/d' $CONF_F
	if test -n "$dnslog"; then
		echo "log-queries" >> $CONF_F
	fi

	sed -i '/log-dhcp/d' $CONF_F
	if test -n "$dhcplog"; then
		echo "log-dhcp" >> $CONF_F
	fi

	if rcdnsmasq status >& /dev/null; then
		rcdnsmasq reload >& /dev/null
	fi
fi

#enddebug
gotopage /cgi-bin/net_services.cgi
