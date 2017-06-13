#!/bin/sh

. common.sh
check_cookie
read_args

DNSMASQ_F=/etc/dnsmasq.conf
DNSMASQ_O=/etc/dnsmasq-opts
DNSMASQ_R=/etc/dnsmasq-resolv
FLG_MSG="#!in use by dnsmasq, don't change"

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
	if ! arping -Dw 2 $hostip >& /dev/null; then
		msg "The IP $hostip is already in use by another computer."
	fi
fi

html_header "Reconfiguring network..."
echo '<h4 class="warn" id="msgid"></h4>'
busy_cursor_start

domain=$(httpd -d "$domain")
hostname=$(httpd -d "$hostname")

if test -z "$mtu"; then mtu=1500; fi
if test -z "$hostname"; then hostname=$(cat /tmp/board); fi
if test -z "$domain"; then domain="localnet"; fi
if test -z "$ns1"; then ns1=$gateway; fi

hostname $hostname
echo $hostname > /etc/hostname

# remove entries with oldip and oldname 
sed -i "/^[^#].*$oldname$/d" $CONFH
sed -i "/^$oldip[ \t]/d" $CONFH
# even if incorrect with old ip (dhcp), host and domain are correct
echo "$oldip $hostname.$domain $hostname" >> $CONFH

if test -z "$dnsmasq_flg"; then
	if test "$iptype" = "static"; then
		echo -e "search $domain\nnameserver $ns1" > $CONFR
		if test -n "$ns2"; then echo "nameserver $ns2" >> $CONFR; fi
	else
		echo "search $domain" > $CONFR-
		for i in $ns1 $ns2; do
			if grep -q "$i #!# DHCP" $CONFR; then
				echo "nameserver $i #!# DHCP" >> $CONFR-
			else
				echo "nameserver $i" >> $CONFR-
			fi
		done
		mv $CONFR- $CONFR
	fi
else
	cat<<-EOF > $CONFR
		$FLG_MSG
		search $domain
		nameserver 127.0.0.1
		#!nameserver $ns1
	EOF
	if test -n "$ns2"; then echo "#!nameserver $ns2" >> $CONFR; fi
	test -f $DNSMASQ_R && echo -e "search $domain\nnameserver $ns1" > $DNSMASQ_R
	test -f $DNSMASQ_R && test -n "$ns2" && echo "nameserver $ns2" >> $DNSMASQ_R
fi

if test "$iptype" = "static"; then
	eval $(ipcalc -n "$hostip" "$netmask") # evaluate NETWORK
	eval $(ipcalc -b "$hostip" "$netmask") # evaluate  BROADCAST

	test -f $DNSMASQ_F && sed -i '/^domain=/d' $DNSMASQ_F
	test -f $DNSMASQ_F && echo "domain=$domain" >> $DNSMASQ_F
	test -f $DNSMASQ_O && sed -i '/^option:router,/d' $DNSMASQ_O
	test -f $DNSMASQ_O && echo "option:router,$gateway	# default route" >> $DNSMASQ_O
	
	# remove any hosts with same name or ip
	sed -i "/[[:space:]]$hostname$/d" $CONFH
	sed -i "/^$hostip[[:space:]]/d" $CONFH
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

cross=0
if test "$iptype" != "$oldiptype"; then
	cross=1 # cross-origin, can't set url
elif test "$iptype" = "dhcp" -a "$hostname" != "$oldname"; then
	cross=1
elif test "$iptype" = "static" -a "$hostip" != "$oldip"; then
	cross=1
fi

if test "$iptype" = "static"; then
		hname=$hostip
else
		hname=$hostname
fi

cat<<-EOF
	<script type="text/javascript">
	var count = 10;
	var cross = $cross
	var port = location.port
	if (port != "")
		port = ":" + port
	var server = location.protocol + "//" + "$hname" + port
	var page = server + "/cgi-bin/host.cgi"
	var testimg = server + "/help.png?" + Math.random()

	function testServer() {    
		var img = new Image()

		img.onload = function() {
			document.body.style.cursor = '';
			if (img.naturalHeight > 0) {
				if (cross) {
					parent.document.location.replace(server)
				}
				else
					window.location.assign(page)
			}
		}

		img.onerror = function() {
			if (count) {
				count--
				setTimeout(testServer, 1000)
			} else {
				document.body.style.cursor = '';
				document.getElementById('msgid').innerHTML = "Timeout, try pointing your browser to <em>" + server + "</em>"
			}
		}
		img.src = testimg
	}

	if (cross) {
		document.getElementById('msgid').innerHTML = 'The box IP, name or protocol have changed.<br>If the page does not load within a minute, point your browser to <em>' + server + '</em><br>or consult your DHCP server to know the box new IP.<br>If using https the browser might complain that the new connection is insecure.'
	}

	setTimeout(testServer, 10000)
	</script></body></html>
EOF

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

firstboot /cgi-bin/host.cgi
