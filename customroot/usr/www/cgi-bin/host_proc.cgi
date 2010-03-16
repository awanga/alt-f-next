#!/bin/sh

. common.sh
check_cookie
read_args

DNSMASQ_F=/etc/dnsmasq.conf
DNSMASQ_O=/etc/dnsmasq-opts

#debug

network=$(echo $hostip | awk -F. '{printf "%d.%d.%d.", $1,$2,$3}')
hostdesc=$(echo $hostdesc | sed 's/+/ /g')
eval $(ipcalc -b $hostip $netmask)
broadcast=$BROADCAST
workgroup=$(httpd -d "$workgroup")

hostname $hostname.$workgroup
echo $hostname > /etc/hostname

sed -i '/^domain=/d' $DNSMASQ_F
echo "domain=$workgroup" >> $DNSMASQ_F
sed -i '/^option:router,/d' $DNSMASQ_O
echo "option:router,$gateway	# default route" >> $DNSMASQ_O

if test "$iptype" = "static"; then

	FLG_MSG="#!in use by dnsmasq, don't change"
	if test -z "$cflg"; then
		echo -e "search $workgroup\nnameserver $ns1\nnameserver $ns2" > /etc/resolv.conf
	else
		echo -e "$FLG_MSG\nnameserver 127.0.0.1\nsearch $workgroup\n#!nameserver $ns1\n#!nameserver $ns2" > /etc/resolv.conf
		echo -e "search $workgroup\nnameserver $ns1\nnameserver $ns2" > /etc/dnsmasq-resolv
	fi
	
	sed -i "/ $hostname$/d" /etc/hosts
	sed -i "/^$hostip/d" /etc/hosts
	echo "$hostip $hostname.$workgroup $hostname" >> /etc/hosts
	
	sed -i 's|A:192.168.1.|A:'$network'|' /etc/httpd.conf
	sed -i "s/workgroup =.*$/workgroup = $workgroup/" /etc/samba/smb.conf
#sed -i "s/interfaces =.*$/interfaces = eth0 $hostip\/$netmask/" /etc/samba/smb.conf
	sed -i "s/hosts allow =.*$/hosts allow = 127. $network/" /etc/samba/smb.conf
	sed -i "s/server string =.*$/server string = $hostdesc/" /etc/samba/smb.conf
	
# FIXME: the following might not be enough.
# FIXME: Add 'reload' to all /etc/init.d scripts whose daemon supports it
	if test -n "$(pidof smbd)"; then
		kill -HUP $(pidof smbd)
	fi

	if test -n "$(pidof udhcpc)"; then
		kill $(pidof udhcpc)
	fi

	if test -n "$(pidof dnsmasq)"; then
		rcdnsmasq reload
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

else
    cat<<-EOF > /etc/network/interfaces
auto lo
  iface lo inet loopback

auto eth0
iface eth0 inet dhcp
  client udhcpc
  mtu $mtu
EOF
fi

rcnetwork restart >/dev/null 2>&1

#debug
gotopage /cgi-bin/host.cgi

