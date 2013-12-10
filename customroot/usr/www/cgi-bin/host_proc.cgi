#!/bin/sh

. common.sh
check_cookie
read_args

DNSMASQ_F=/etc/dnsmasq.conf
DNSMASQ_O=/etc/dnsmasq-opts
DNSMASQ_R=/etc/dnsmasq-resolv

CONFH=/etc/hosts
CONFR=/etc/resolv.conf
CONFS=/etc/samba/smb.conf
CONFHTTP=/etc/httpd.conf
CONFINT=/etc/network/interfaces
CONF_MODPROBE=/etc/modprobe.conf
CONF_MISC=/etc/misc.conf

#debug

if test -f $CONF_MODPROBE; then
	sed -i '/^blacklist.*ipv6/d' $CONF_MODPROBE
fi

if test -f "$CONF_MISC"; then
	sed -i '/^MODLOAD_IPV6=/d' $CONF_MISC
fi

if test -z "$ipv6"; then
	echo "blacklist ipv6" >> $CONF_MODPROBE
	sed -i '/::/d' $CONFH
else
	echo "MODLOAD_IPV6=y" >> $CONF_MISC
	modprobe ipv6 >& /dev/null
	if ! grep -q ipv6-localhost $CONFH; then
	cat<<-EOF >> $CONFH
		::1	localhost ipv6-localhost ipv6-loopback
		fe00::0	ipv6-localnet
		ff00::0	ipv6-mcastprefix
		ff02::1	ipv6-allnodes
		ff02::2	ipv6-allrouters
		ff02::3	ipv6-allhosts
	EOF
	fi
fi

if test "$iptype" = "static"; then
	arping -Dw 2 $hostip >& /dev/null
	if test $? = 1; then
		msg "IP $hostip seems to be already in use"
	fi
fi

html_header
busy_cursor_start

domain=$(httpd -d "$domain")
hostname=$(httpd -d "$hostname")

if test -z "$mtu"; then mtu=1500; fi
if test -z "$hostname"; then hostname="DNS-323"; fi
if test -z "$domain"; then domain="localnet"; fi

hostname $hostname
echo $hostname > /etc/hostname

# remove entries with oldip and oldname 
sed -i "/^[^#].*$oldnm$/d" $CONFH
sed -i "/^$oldip[ \t]/d" $CONFH
# even if incorrect with old ip (dhcp), host and domain are correct
echo "$oldip $hostname.$domain $hostname" >> $CONFH

if test "$iptype" = "static"; then
	eval $(ipcalc -n "$hostip" "$netmask") # evaluate NETWORK
	eval $(ipcalc -b "$hostip" "$netmask") # evaluate  BROADCAST

	sed -i '/^domain=/d' $DNSMASQ_F
	echo "domain=$domain" >> $DNSMASQ_F
	sed -i '/^option:router,/d' $DNSMASQ_O
	echo "option:router,$gateway	# default route" >> $DNSMASQ_O

	FLG_MSG="#!in use by dnsmasq, don't change"
	if test -z "$cflg"; then
		echo -e "search $domain\nnameserver $ns1" > $CONFR
		if test -n "$ns2"; then echo "nameserver $ns2" >> $CONFR; fi
	else
		echo -e "$FLG_MSG\nnameserver 127.0.0.1\nsearch $domain\n#!nameserver $ns1\n#!nameserver $ns2" > $CONFR
		if test -n "$ns2"; then echo "#!nameserver $ns2" >> $CONFR; fi
		echo -e "search $domain\nnameserver $ns1\nnameserver $ns2" > $DNSMASQ_R
		if test -n "$ns2"; then echo "nameserver $ns2" >> $DNSMASQ_R; fi
	fi
	
	# remove any hosts with same name or ip
	sed -i "/ $hostname$/d" $CONFH
	sed -i "/^$hostip/d" $CONFH
	echo "$hostip $hostname.$domain $hostname" >> $CONFH

	sed -i "s|^A:.*#!# Allow local net.*$|A:$NETWORK/$netmask #!# Allow local net|" $CONFHTTP
	sed -i "s|hosts allow = \([^ ]*\) \([^ ]*\)\(.*$\)|hosts allow = 127. $NETWORK/${netmask}\3|" $CONFS

	if test -n "$gateway"; then igw="gateway $gateway"; fi

	cat<<-EOF > $CONFINT
	auto lo
	  iface lo inet loopback

	auto eth0
	iface eth0 inet static
	  address $hostip
	  netmask $netmask
	  broadcast $BROADCAST
	  mtu $mtu
	  $igw
	EOF

else

	cat<<-EOF > $CONFINT
	auto lo
	  iface lo inet loopback

	auto eth0
	iface eth0 inet dhcp
	  client udhcpc
	  mtu $mtu
	  address $oldip
	  hostname $hostname
	EOF
fi

if test -f /var/run/udhcpc.eth0.pid; then
	kill $(cat /var/run/udhcpc.eth0.pid) >& /dev/null
fi
ifdown -f eth0 >& /dev/null
ifup -f eth0 >& /dev/null

# FIXME: the following might not be enough.
# FIXME: Add 'reload' to all /etc/init.d scripts whose daemon supports it

if rcsmb status >& /dev/null; then
	# samba-3.5.12 does not change workgroup or server string on reload...
	#rcsmb reload >& /dev/null
	rcsmb restart >& /dev/null
fi

if rcdnsmasq status >& /dev/null; then
	rcdnsmasq reload  >& /dev/null
fi

busy_cursor_end

#enddebug

js_gotopage /cgi-bin/host.cgi
