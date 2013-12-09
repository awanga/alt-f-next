#!/bin/sh

. common.sh
check_cookie
write_header "DHCP/DNS Setup"

CONF_H=/etc/dnsmasq-hosts
CONF_O=/etc/dnsmasq-opts
CONF_F=/etc/dnsmasq.conf
RESOLV=/etc/resolv.conf
CONFNTP=/etc/ntp.conf
CONFM=/etc/misc.conf

if ! test -e $CONF_H; then touch $CONF_H; fi

if test -f $CONFM; then
	. $CONFM
fi
if test -z "$NTPD_DAEMON" -o "$NTPD_DAEMON" = "no"; then
	dislntp=disabled
fi

hostip=$(hostname -i)
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
hostnm=$(hostname -s)
hostfnm=$(hostname -f)
#eval $(ipcalc -ns $hostip $netmask)
#net=$(echo $NETWORK | cut -d. -f1-3)

eval $(awk -F"," '/dhcp-range=/{printf "lrg=%s; hrg=%s; lease=%s",
	 substr($1,12), $2, $3}' $CONF_F)

cat <<-EOF
	<script type="text/javascript">
	function toogle_ntp(st) {
		if (st == "true")
			stt = true
		else
			stt = false
		document.dnsmasq.ntp_entry.disabled = stt;
	}
	function toogle_tftp(theform) {
		st = document.dnsmasq.tftp.checked == true ? false : true
		document.dnsmasq.tftproot.disabled = st
		document.dnsmasq.ftpbrowse.disabled = st
	}
	function getMAC(mac_id, ip_id) {
		ip = document.getElementById(ip_id).value
		window.open("get_mac.cgi?id=" + mac_id + "?ip=" + ip, "GetMAC", "width=300,height=100");
		return false
	}
	</script>

	<form name=dnsmasq action="/cgi-bin/dnsmasq_proc.cgi" method="post">
	<fieldset><legend>Dynamically serve IPs</legend><table>
	<tr><td> From IP</td><td><input type=text size=12 name=low_rg value="$lrg"></td></tr>
	<tr><td>To IP</td><td><input type=text size=12 name=high_rg value="$hrg"></td></tr>
	<tr><td>Lease Time: </td><td><input type=text size=4 name=lease value="$lease"></td></tr>
	</table></fieldset>

	<fieldset><legend>Serve fixed IPs based on MAC</legend>
	<table><tr align=center>
	<td> <strong> Name </strong> </td><td> <strong> IP </strong> </td><td> <strong> Get MAC </strong> </td>
	<td> <strong> MAC </strong> </td><td> <strong> Lease </strong> </td></tr>
EOF

oifs="$IFS"; IFS=","; cnt=0
while read mac nm ip lease rest; do
    if test -z "$mac" -o ${mac#\#} != $mac; then continue; fi
    if test "$nm" = "$hostnm"; then continue; fi

	cat<<-EOF
    	<tr><td><input size=12 type=text name="nm_$cnt" value="$nm"></td>
		<td><input size=12 type=text id="ip_$cnt" name="ip_$cnt" value="$ip"></td>
		<td><input type=submit name="_$cnt" value="Get" onclick="return getMAC('mac_$cnt','ip_$cnt')"></td>
		<td><input size=18 type=text id="mac_$cnt" name="mac_$cnt" value="$mac"></td>
		<td><input size=4 type=text name="lease_$cnt" value="$lease"></td></tr>
	EOF
    cnt=$((cnt+1))
done < $CONF_H

IFS=$oifs
for i in $(seq $cnt $((cnt+2))); do
	cat<<-EOF
		<tr><td><input size=12 type=text name="nm_$i"></td>
		<td><input size=12 type=text id="ip_$i" name="ip_$i"></td>
		<td><input type=submit name="_$i" value="Get" onclick="return getMAC('mac_$i','ip_$i')"></td>
		<td><input size=17 type=text id="mac_$i" name="mac_$i"></td>
		<td><input size=4 type=text name="lease_$i"></td></tr>
	EOF
done

cat<<-EOF
	</table></fieldset>
	<input type=hidden name=cnt_din value="$i">

	<fieldset><legend>Current Leases</legend>
EOF

	if ! test -s /tmp/dnsmasq.leases; then
		echo "None"
	else
		echo "<table><tr><th width=100px>Name</th><th width=100px>IP</th><th width=130px>MAC</th><th>Expiry date</th></tr>"
		while read exp mac ip name b; do
			dexp="$(awk 'BEGIN{print strftime("%b %d, %R",'$exp')}')"
			echo "<tr><td>$name</td><td>$ip</td><td>$mac</td><td>$dexp</td></tr>"
		done < /tmp/dnsmasq.leases
		echo "</table>"
	fi

cat <<EOF
	</fieldset>
	<input type=hidden name=cnt_know value="$i">
EOF

if false; then
	echo "<fieldset><legend>Forward DNS Servers</legend>"

	FLG_MSG="#!in use by dnsmasq, don't change"
	if $(grep -q "$FLG_MSG" $RESOLV); then
		stk="#!nameserver"
	else
		stk="nameserver"
	fi
	i=0
	while read tk ns; do
		if test -z "$tk"; then continue; fi
		if test "$tk" != $stk -o -z "$ns"; then continue; fi
		echo "Server $((i+1)) <input type=text readonly size=12 name=ns_$i value=$ns><br>"
		i=$((i+1))
	done  < $RESOLV
	echo "</fieldset>"
fi

if test -e $CONFNTP; then 
	while read ntp_srv host; do
		if test "$ntp_srv" = "server" -a "$host" != "127.127.1.0"; then
			break
		fi
	done < $CONFNTP
fi

ntp_advert="$(grep '^option:ntp-server' $CONF_O | tr ',\t' ' ' | cut -f2 -d' ')"

chkentp="disabled"
if test -z "$ntp_advert"; then
	chknntp="checked"
elif test "$ntp_advert" = "0.0.0.0"; then
	chklntp="checked"
else
	chksntp="checked"
	chkentp=""
fi

cat<<-EOF
	<fieldset><legend>Time Servers</legend><table>
	<tr>
		<td><input type=radio $chknntp name=ntp value=no onchange="toogle_ntp('true')"></td>
		<td colspan=2>Don't advertise any server</td></tr>
	<tr>
		<td><input type=radio $chklntp $dislntp name=ntp value=local onchange="toogle_ntp('true')"></td>
		<td colspan=2>Advertise local NTP server</td></tr>
	<tr>
		<td><input type=radio $chksntp name=ntp value=server onchange="toogle_ntp('false')"></td>
		<td>Advertise NTP server</td>
		<td><input type=text $chkentp name=ntp_entry size=12 value="$host"></td></tr>
	</table></fieldset>
EOF

eval $(awk -F= '/enable-tftp/{print "tftp=checked"} \
		/tftp-root/{printf "tftproot=%s", substr($0,index($0,$2))}' $CONF_F)
tftproot=$(httpd -e "$tftproot")
if test -z "$tftp"; then
	tftpdis=disabled
fi

cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
		    start_dir = document.getElementById(input_id).value;
		    if (start_dir == "")
		    	start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
	</script>
	<fieldset><legend>TFTP server</legend>
	<table>
	<tr><td>Enable TFTP</td><td><input type=checkbox $tftp value=tftp name=tftp onchange="toogle_tftp()"></td></tr>
	<tr><td>Root Folder</td>
		<td><input id=tftproot $tftpdis type=text size=20 name=tftproot value="$tftproot">
		<input type=button $tftpdis name=ftpbrowse onclick="browse_dir_popup('tftproot')" value=Browse>
		</td></tr>
	</table></fieldset>
EOF

eval $(awk '/log-queries/{print "dnslog=CHECKED"} \
		/log-dhcp/{print "dhcplog=CHECKED"}' $CONF_F)

cat<<EOF	
	<fieldset><legend>Logging</legend><table>
	<tr><td>Log DNS queries</td>
		<td><input type=checkbox $dnslog name=dnslog value=true></td></tr>
	<tr><td>Log DHCP queries</td>
		<td><input type=checkbox $dhcplog name=dhcplog value=true></td></tr>
	</table></fieldset>
	<p><input type=hidden name=cnt_dns value="$i">
	<input type=submit name=submit value=Submit>$(back_button)
	</form></body></html>
EOF
