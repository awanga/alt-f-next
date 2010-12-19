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

#debug

if test "$iptype" = "static"; then
	arping -Dw 2 $hostip >& /dev/null
	if test $? = 1; then
		msg "IP $hostip seems to be already in use"
	fi
fi

html_header
busy_cursor_start

hostdesc=$(httpd -d $hostdesc)
workgp=$(httpd -d "$workgp")

hostname $hostname.$workgp
echo $hostname > /etc/hostname

# remove entries with oldip and oldname 
sed -i "/^[^#].*$oldnm$/d" $CONFH
sed -i "/^$oldip[ \t]/d" $CONFH
# even if incorrect with old ip (dhcp), host and domain are correct
echo "$oldip $hostname.$workgp $hostname" >> $CONFH

#sed -i '/^A:.*\.$/d' $CONFHTTP
sed -i "s/^workgroup =.*$/workgroup = $workgp/" $CONFS
sed -i "s/^server string =.*$/server string = $hostdesc/" $CONFS

if test "$iptype" = "static"; then
	eval $(ipcalc -n "$hostip" "$netmask") # evaluate NETWORK
	eval $(ipcalc -b "$hostip" "$netmask") # evaluate  BROADCAST

	sed -i '/^domain=/d' $DNSMASQ_F
	echo "domain=$workgp" >> $DNSMASQ_F
	sed -i '/^option:router,/d' $DNSMASQ_O
	echo "option:router,$gateway	# default route" >> $DNSMASQ_O

	FLG_MSG="#!in use by dnsmasq, don't change"
	if test -z "$cflg"; then
		echo -e "search $workgp\nnameserver $ns1" > $CONFR
		if test -n "$ns2"; then echo "nameserver $ns2" >> $CONFR; fi
	else
		echo -e "$FLG_MSG\nnameserver 127.0.0.1\nsearch $workgp\n#!nameserver $ns1\n#!nameserver $ns2" > $CONFR
		if test -n "$ns2"; then echo "#!nameserver $ns2" >> $CONFR; fi
		echo -e "search $workgp\nnameserver $ns1\nnameserver $ns2" > $DNSMASQ_R
		if test -n "$ns2"; then echo "nameserver $ns2" >> $DNSMASQ_R; fi
	fi
	
	# remove any hosts with same name or ip
	sed -i "/ $hostname$/d" $CONFH
	sed -i "/^$hostip/d" $CONFH
	echo "$hostip $hostname.$workgp $hostname" >> $CONFH

	sed -i "s|^A:.*#!# Allow local net.*$|A:$NETWORK/$netmask #!# Allow local net|" $CONFHTTP
	sed -i "s|hosts allow =.*$|hosts allow = 127. $NETWORK/$netmask|" $CONFS

# FIXME: the following might not be enough.
# FIXME: Add 'reload' to all /etc/init.d scripts whose daemon supports it

	start-stop-daemon -K -x udhcpc >& /dev/null

	if rcsmb status >& /dev/null; then
		rcsmb reload  >& /dev/null
	fi

	if rcdnsmasq status >& /dev/null; then
		rcdnsmasq reload  >& /dev/null
	fi

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
	EOF
fi

ifdown eth0 >& /dev/null
sleep 1
ifup eth0 >& /dev/null
sleep 3

busy_cursor_end

#enddebug

if test "$(cat /etc/TZ)" = "NONE-0" -a -f /tmp/firstboot; then
	js_gotopage /cgi-bin/time.cgi
else
	js_gotopage /cgi-bin/host.cgi
fi

echo "</body></html>"
