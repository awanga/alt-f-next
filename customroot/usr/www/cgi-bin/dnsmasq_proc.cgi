#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_H=/etc/dnsmasq-hosts
CONF_O=/etc/dnsmasq-opts
CONF_F=/etc/dnsmasq.conf
HOSTS=/etc/hosts
#CONF_R=/etc/dnsmasq-resolv
CONF_NTP=/etc/ntp.conf

if test -n "$Get"; then
	ip=$(eval echo \$ip$Get)
	name=$(eval echo \$nm$Get)

	if test -z "$ip"; then
		msg "You must supply an host ip to get its MAC"
	elif ! checkip $ip; then
		msg "The IP must be in the form x.x.x.x, where x is from 1 to 3 digits"
	else
		ping -W 3 -c 2 $ip >/dev/null 2>&1
		if test $? = 1; then
			msg "Host with ip $ip is not answering"
		else
			res=$(arp -n $ip)
			if test "$(echo $res | cut -d" " -f1,2,3)" = "No match found"; then
				msg "Host $name with ip $ip is alive but couldnt get its MAC"
			else
				lease=$(eval echo \$lease_$GetMAC)
				mac=$(echo $res | cut -d" " -f 4)
				msg "MAC of host $name with ip=$ip is $mac"
			fi
		fi
	fi

elif test -n "$Submit"; then
	if test -z "$high_rg" -o -z "$low_rg" -o -z "$lease"; then
		msg "Ip start, IP end and Lease all must be specified"
	elif ! $(checkip $high_rg); then
		msg "The start IP must be in the form x.x.x.x, where x is from 1 to 3 digits"
	elif ! $(checkip $low_rg); then
		msg "The end IP must be in the form x.x.x.x, where x is from 1 to 3 digits"
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
	for i in $(seq 0 $cnt_ntp); do
		ntp=$(eval echo \$ntp_$i)
		if test -z "$ntp"; then continue; fi
		res="$(nslookup $ntp)"
		if test $? = 0; then
			ntph=$(echo "$res" | awk '/Address/{ if (NR == 5) print $3}')
			echo "option:ntp-server,$ntph	# ntp server" >> $CONF_O
		fi
	done

	echo > $CONF_H
	for i in $(seq 0 $cnt_din); do
		nm=$(eval echo \$nm_$i)
		ip=$(eval echo \$ip_$i)
		mac=$(httpd -d "$(eval echo \$mac_$i)")
		lease=$(eval echo \$lease_$i)

		if test -z "$nm" -o -z "$ip" -o -z "$mac"; then continue; fi
		
		if ! $(checkname $nm); then
			msg "The host name can only have letters and digits, no spaces, and must begin with a letter"
		elif ! $(checkip $ip); then
			msg "The IP must be in the form x.x.x.x, where x is from 1 to 3 digits"
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

	echo "127.0.0.1	localhost" > $HOSTS

	for i in $(seq 0 $cnt_know); do
		nm=$(eval echo \$knm_$i)
		ip=$(eval echo \$kip_$i)

		if test -z "$nm" -o -z "$ip"; then continue; fi
		if ! $(checkname $nm); then
			msg "The host name can only have letters and digits, no spaces, and must begin with a letter"
		elif ! $(checkip $ip); then
			msg "The IP must be in the form x.x.x.x, where x is from 1 to 3 digits"
		fi

		echo "$ip	$nm.$net	$nm" >> $HOSTS
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

	rcdnsmasq reload > /dev/null 2>&1
fi

#  if grep -q -e $ip -e "$name " $HOSTS; then
#    msg "An host with IP $ip or/and name $name already exists"
#  fi
#
#  if grep -q $ip $CONF_H; then
#     msg "An host with IP $ip already exists"
#  fi

#enddebug
gotopage /cgi-bin/net_services.cgi
