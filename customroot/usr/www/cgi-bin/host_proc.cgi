#!/bin/sh

. common.sh
check_cookie
read_args

DNSMASQ_F=/etc/dnsmasq.conf
DNSMASQ_O=/etc/dnsmasq-opts

#debug

#hostdesc=$(echo $hostdesc | sed 's/+/ /g')
hostdesc=$(httpd -d $hostdesc)
workgroup=$(httpd -d "$workgroup")

hostname $hostname.$workgroup
echo $hostname > /etc/hostname

# remove entries with oldip and oldname 
sed -i "/^[^#].*$oldnm$/d" /etc/hosts
sed -i "/^$oldip[ \t]/d" /etc/hosts
# even if incorrect with old ip (dhcp), host and domain are correct
echo "$oldip $hostname.$workgroup $hostname" >> /etc/hosts

sed -i '/^A:.*\.$/d' /etc/httpd.conf
sed -i "s/workgroup =.*$/workgroup = $workgroup/" /etc/samba/smb.conf
sed -i "s/server string =.*$/server string = $hostdesc/" /etc/samba/smb.conf

if test "$iptype" = "static"; then
	network=$(echo $hostip | awk -F. '{printf "%d.%d.%d.", $1,$2,$3}')
	eval $(ipcalc -b "$hostip" "$netmask")
	broadcast=$BROADCAST

	sed -i '/^domain=/d' $DNSMASQ_F
	echo "domain=$workgroup" >> $DNSMASQ_F
	sed -i '/^option:router,/d' $DNSMASQ_O
	echo "option:router,$gateway	# default route" >> $DNSMASQ_O

	FLG_MSG="#!in use by dnsmasq, don't change"
	if test -z "$cflg"; then
		echo -e "search $workgroup\nnameserver $ns1" > /etc/resolv.conf
		if test -n "$ns2"; then echo "nameserver $ns2" >> /etc/resolv.conf; fi
	else
		echo -e "$FLG_MSG\nnameserver 127.0.0.1\nsearch $workgroup\n#!nameserver $ns1\n#!nameserver $ns2" > /etc/resolv.conf
		if test -n "$ns2"; then echo "#!nameserver $ns2" >> /etc/resolv.conf; fi
		echo -e "search $workgroup\nnameserver $ns1\nnameserver $ns2" > /etc/dnsmasq-resolv
		if test -n "$ns2"; then echo "nameserver $ns2" >> /etc/dnsmasq-resolv; fi
	fi
	
	# remove any hosts with same name or ip
	sed -i "/ $hostname$/d" /etc/hosts
	sed -i "/^$hostip/d" /etc/hosts
	echo "$hostip $hostname.$workgroup $hostname" >> /etc/hosts
	
	echo  "A:$network" >> /etc/httpd.conf
	sed -i "s/hosts allow =.*$/hosts allow = 127. $network/" /etc/samba/smb.conf

# FIXME: the following might not be enough.
# FIXME: Add 'reload' to all /etc/init.d scripts whose daemon supports it
# FIXME: this and some other setting above should be done by the rcnetwork

	#if pidof udhcpc >& /dev/null; then
	#	kill $(pidof udhcpc) >& /dev/null
	#fi

	start-stop-daemon -K -x udhcpc >& /dev/null

	if rcsmb status >& /dev/null; then
		rcsmb reload  >& /dev/null
	fi

	if rcdnsmasq status >& /dev/null; then
		rcdnsmasq reload  >& /dev/null
	fi
		
	cat<<-EOF > /etc/network/interfaces
	auto lo
	  iface lo inet loopback

	auto eth0
	iface eth0 inet static
	  address $hostip
	  netmask $netmask
	  broadcast $broadcast
	  gateway $gateway
	  mtu $mtu
	EOF

else # FIXME: not enought, the udhcpc script should do updates
	cat<<-EOF > /etc/network/interfaces
	auto lo
	  iface lo inet loopback

	auto eth0
	iface eth0 inet dhcp
	  client udhcpc
	EOF
fi

# the dhcp client script /usr/share/udhcpc/default.script must configure what is missing
ifdown eth0 >& /dev/null
sleep 1
ifup eth0 >& /dev/null
sleep 3

#debug

if test "$(cat /etc/TZ)" = "NONE-0" -a -f /tmp/firstboot; then
	gotopage /cgi-bin/time.cgi
else
	gotopage /cgi-bin/host.cgi
fi
