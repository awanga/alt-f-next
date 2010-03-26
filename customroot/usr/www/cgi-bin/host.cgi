#!/bin/sh

. common.sh
check_cookie
write_header "Host Setup"

if test -f /tmp/firstboot; then
	cat<<-EOF
		<center>
		<h3>Welcome to your first login to Alt-F</h3>
		<h4>You should now fill all the host details
		and Submit them</h4>
		</center>
	EOF
fi

RESOLV=/etc/resolv.conf

FLG_MSG="#!in use by dnsmasq, don't change"
if $(grep -q "$FLG_MSG" $RESOLV); then
        stk="#!nameserver"; cflg=1
else
        stk="nameserver"
fi

if test -e /etc/resolv.conf; then
    eval $(awk 'BEGIN{i=1} /^'$stk'/{print "ns" i "=" $2; i++}' $RESOLV)
else
    ns1=""
    ns2=""
fi

if test -e /etc/samba/smb.conf; then
    eval $(awk '/server string/{split($0, a, "= ");
        print "hostdesc=\"" a["2"] "\""}' /etc/samba/smb.conf)
        
    eval $(awk '/workgroup/{split($0, a, "= ");
        print "workgroup=\"" a["2"] "\""}' /etc/samba/smb.conf)
else
    hostdesc=""
    workgroup=""
fi

ifconfig eth0 >/dev/null 2>&1
if test $? = 0; then
    hostname=$(hostname -s)
#    hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
    hostip=$(hostname -i)
    netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
    bcast=$(ifconfig eth0 | awk '/inet addr/ { print substr($3, 7) }')
    gateway=$(route -n | awk '$1 == "0.0.0.0" { print $2 }')
    mtu=$(ifconfig eth0 | awk '/MTU/{print substr($5,5)}')
fi

cat<<-EOF
	<script type="text/javascript">
	function toogle(theform) {
		for (var i = 0; i < theform.length; i++) {
			if (theform.elements[i].id == "sip")
				theform.elements[i].disabled = theform.elements[i].disabled ? false : true;
		}
	}
	</script>

    <form name=sipf action="/cgi-bin/host_proc.cgi" method="post">
    <table>
    <tr><td>Host name:</td>
        <td><input type=text name=hostname value=$hostname></td></tr>
    <tr><td>Host description:</td>
        <td><input type=text name=hostdesc value="$hostdesc"></td></tr>
    <tr><td>Work Group:</td>
        <td><input type=text name=workgroup value="$workgroup"></td></tr>

    <tr><td><br></td><td></td></tr>
    <tr>
        <td>Static IP<input type=radio CHECKED name=iptype value=static onchange="toogle(sipf)"></td>
        <td>DHCP<input type=radio name=iptype value=dhcp onchange="toogle(sipf)"></td>
    </tr>

    <tr><td>Host IP:</td><td><input type=text id=sip name=hostip value=$hostip></td></tr>
    <tr><td>Netmask:</td><td><input type=text id=sip name=netmask value=$netmask></td></tr>
    <tr><td>Gateway:</td><td><input type=text id=sip name=gateway value=$gateway></td></tr>
    <tr><td>Name server 1:</td><td><input type=text id=sip name=ns1 value=$ns1></td></tr>
    <tr><td>Name server 2:</td><td><input type=text id=sip name=ns2 value=$ns2>
	<input type=hidden name=cflg value="$cflg"></td></tr>

    <tr><td>Frame size:</td><td><input type=text id=sip name=mtu value=$mtu></td></tr>

    <tr><td></td><td><input type="submit" value="Submit"></td></tr>
    </table>

    </form>        
    </body>
    </html>
EOF
