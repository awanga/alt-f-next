#!/bin/sh

. common.sh
check_cookie
write_header "Host Setup"

RESOLV=/etc/resolv.conf
CONFS=/etc/samba/smb.conf
CONFINT=/etc/network/interfaces

if test -f /tmp/firstboot; then
	cat<<-EOF
		<center>
		<h3>Welcome to your first login to Alt-F</h3>
		<h4>You should now fill all the host details
		and Submit them</h4>
		</center>
	EOF
fi

FLG_MSG="#!in use by dnsmasq, don't change"
if $(grep -q "$FLG_MSG" $RESOLV); then
	stk="#!nameserver"; cflg=1
else
	stk="nameserver"
fi

if test -e $RESOLV; then
	eval $(awk 'BEGIN{i=1} /^'$stk'/{print "ns" i "=" $2; i++}' $RESOLV)
else
	ns1=""
	ns2=""
fi

if test -e $CONFS; then
	eval $(awk '/server string/{split($0, a, "= ");
		print "hostdesc=\"" a["2"] "\""}
		/workgroup/{split($0, a, "= ");
		print "workgp=\"" a["2"] "\""}' $CONFS)
else
	hostdesc=""
	workgp=""
fi

ifconfig eth0 >/dev/null 2>&1
if test $? = 0; then
	hostname=$(hostname -s)
	hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
	netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
	bcast=$(ifconfig eth0 | awk '/inet addr/ { print substr($3, 7) }')
	gateway=$(route -n | awk '$1 == "0.0.0.0" { print $2 }')
	mtu=$(ifconfig eth0 | awk '/MTU/{print substr($0, match($a,"MTU")+4,5)}')
fi

mktt mtu_tt "Also called jumbo frames"

cat<<-EOF
	<script type="text/javascript">
	function edisable(state) {
		sipf=document.getElementById("sipf");
		if (state == true) {
			document.getElementById("dhcp").checked = true;
			document.getElementById("static").checked = false;
		} else {
			document.getElementById("dhcp").checked = false;
			document.getElementById("static").checked = true;
		}
		for (var i = 0; i < sipf.length; i++) {
			if (sipf.elements[i].id == "sip")
				sipf.elements[i].disabled = state;
		}
	}
	function ipchange(oip) {
		ret = true;
		nip = document.getElementById("sip").value;
		stat = document.getElementById("static").checked;
		if (stat == true && oip != nip)
			ret = confirm("Your IP will change. Redirect your " +
			'\n' + "browser to http://" + nip);
		if (stat == false)
			ret = confirm("Your IP will change. Consult your DHCP server to know" +
			 '\n' + "the new IP and redirect your browser it.");
		return ret;
	}
	function mtu_warn() {
		if (document.sipf.mtu.value > 3700)
			alert("Values higher than 3700 can effectively diminish performance")
	}
	</script>

	<form id="sipf" name=sipf action="/cgi-bin/host_proc.cgi" method="post">
	<fieldset><legend><strong>Host details</strong></legend><table>
	<tr><td>Host name:</td>
		<td><input type=text name=hostname value=$hostname></td></tr>
	<tr><td>Host description:</td>
		<td><input type=text name=hostdesc value="$hostdesc"></td></tr>
	<tr><td>Workgroup:</td>
		<td><input type=text name=workgp value="$workgp"></td></tr>

	</table></fieldset><br>

	<fieldset><legend><strong>IP settings</strong></legend><table>
	<tr>
	<td>Static IP<input type=radio id="static" name="iptype" value="static" onclick="edisable(false)"></td>
	<td>DHCP <input type=radio id="dhcp" name="iptype" value="dhcp" onclick="edisable(true)"></td>
	</tr>

	<tr><td>Host IP:</td><td><input type=text id=sip name="hostip" value=$hostip></td></tr>
	<tr><td>Netmask:</td><td><input type=text id=sip name="netmask" value=$netmask></td></tr>
	<tr><td>Gateway:</td><td><input type=text id=sip name="gateway" value=$gateway></td></tr>
	<tr><td>Name server 1:</td><td><input type=text id=sip name="ns1" value=$ns1></td></tr>
	<tr><td>Name server 2:</td><td><input type=text id=sip name="ns2" value=$ns2></tr>
	<tr><td>Frame size:</td><td><input type=text id=sip name="mtu" value=$mtu onchange="mtu_warn()" $(ttip mtu_tt)></td></tr>
	</table></fieldset><br>

	<input type=hidden name=cflg value="$cflg">
	<input type=hidden name=oldip value="$hostip">
	<input type=hidden name=oldnm value="$hostname">
	<input type="submit" value="Submit" onclick="return ipchange('$hostip')">

	</form>
EOF

ipdisable="false"
if $(grep -q '^ *iface.*eth0.*dhcp' $CONFINT); then
	ipdisable="true"
fi

cat<<-EOF
	<script type="text/javascript">
	edisable($ipdisable);
	</script>
	</body></html>
EOF

