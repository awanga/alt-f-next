#!/bin/sh

. common.sh
check_cookie
write_header "Host Setup"

RESOLV=/etc/resolv.conf
CONFINT=/etc/network/interfaces
CONF_MODPROBE=/etc/modprobe.conf

mktt tt_ipv6 "IPv6 is for the next generation internet, most users don't need it.<br>
When checked, after submiting it takes effect immediately<br>
When unchecking, submiting will schedule it for disable at next reboot."

mktt mtu_tt "Also called jumbo frames"

ipdisable="false"
oldiptype="static"
if $(grep -q '^[^#].*face.*eth0.*dhcp' $CONFINT); then
	ipdisable="true"
	oldiptype="dhcp"
fi

if ! modprobe -D ipv6 >& /dev/null; then
	ipv6_dis="disabled"
	ipv6_msg="(You have to install the kernel-modules package)"
fi

if test -f $CONF_MODPROBE; then
	if ! grep -q 'blacklist.*ipv6' $CONF_MODPROBE; then
		ipv6_chk="checked"
	fi
fi

ifout=$(ifconfig eth0 2> /dev/null)

if echo "$ifout"  | grep -q inet6; then
	ipv6_inuse="(currently in use)"
elif test -n "$ipv6_chk"; then
	ipv6_inuse="(not loaded)"
fi

eval $(echo "$ifout" | awk '
	/inet addr:/ { printf ("hostip=%s; ", substr($2, 6)) }
	/inet addr:/ { printf ("netmask=%s; ", substr($4, 6)) }
	/inet addr:/ { printf ("bcast=%s; ", substr($3, 7)) }
	/MTU:/{printf ("mtu=%s", substr($0, match($a,"MTU")+4,4))}
	')

if ! hostname=$(hostname -s 2> /dev/null); then hostname=$(cat /tmp/board); fi
if ! domain=$(hostname -d 2> /dev/null); then domain="localnet"; fi
gateway=$(route -n | awk '$1 == "0.0.0.0" { print $2 }')

FLG_MSG="#!in use by dnsmasq, don't change"
if grep -q "$FLG_MSG" $RESOLV 2> /dev/null; then
	stk="#!nameserver"; dnsmasq_flg=1
else
	stk="nameserver"
fi

ns2=""
if test -e $RESOLV; then
	eval $(awk 'BEGIN{i=1} /^'$stk'/{print "ns" i "=" $2; i++}' $RESOLV)
fi
if test -z "$ns1"; then ns1=$gateway; fi

cat<<-EOF
	<script type="text/javascript">
	function edisable(state) {
		document.getElementById("static").checked = !state
		document.getElementById("dhcp").checked = state;

		for (var i = 1; i < 5; i++)
			document.getElementById("sip" + i).disabled = state
	}
	function mtu_warn() {
		if (document.sipf.mtu.value > 9000) {
			alert("Values higher than 9000 bytes are forbidden.")
			document.sipf.mtu.value = 9000
		}
		else if (document.sipf.mtu.value > 7500)
			alert("Values higher than 7500 bytes waste memory" + '\n' + "and have a small impact on throughput.")
	}
	</script>

	<form id="sipf" name=sipf action="/cgi-bin/host_proc.cgi" method="post">
	<table><tr>
	<td>Static IP<input type=radio id="static" name="iptype" value="static" onclick="edisable(false)"></td>
	<td>DHCP <input type=radio id="dhcp" name="iptype" value="dhcp" onclick="edisable(true)"></td></tr>
	<tr><td>Host name:</td><td><input type=text name=hostname value="$hostname"></td></tr>
	<tr><td>Domain:</td><td><input type=text id=sip1 name="domain" value="$domain"></td></tr>
	<tr><td>Host IP:</td><td><input type=text id=sip2 name="hostip" value="$hostip"></td></tr>
	<tr><td>Netmask:</td><td><input type=text id=sip3 name="netmask" value="$netmask"></td></tr>
	<tr><td>Gateway:</td><td><input type=text id=sip4 name="gateway" value="$gateway"></td></tr>
	<tr><td>Name server 1:</td><td><input type=text name="ns1" value="$ns1"></td></tr>
	<tr><td>Name server 2:</td><td><input type=text name="ns2" value="$ns2"></td></tr>
	<tr><td>Frame size:</td><td><input type=text name="mtu" value="$mtu" onchange="mtu_warn()" $(ttip mtu_tt)></td></tr>
	<tr><td>Enable IPv6:</td><td><input type=checkbox $ipv6_dis $ipv6_chk name="ipv6" value="yes" $(ttip tt_ipv6)> $ipv6_inuse $ipv6_msg</td></tr>
	</table>

	<p><input type=hidden name=dnsmasq_flg value="$dnsmasq_flg">
	<input type=hidden name=oldip value="$hostip">
	<input type=hidden name=oldname value="$hostname">
	<input type=hidden name=oldiptype value="$oldiptype">
	<input type="submit" value="Submit">

	</form>
	<script type="text/javascript">
	edisable($ipdisable);
	</script>
	</body></html>
EOF
