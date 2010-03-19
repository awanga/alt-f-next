#!/bin/sh

. common.sh
check_cookie
write_header "DHCP/DNS Setup"

CONF_H=/etc/dnsmasq-hosts
CONF_O=/etc/dnsmasq-opts
CONF_F=/etc/dnsmasq.conf
RESOLV=/etc/resolv.conf
HOSTS=/etc/hosts
CONFNTP=/etc/ntp.conf

s="<strong>"
es="</strong>"

hostip=$(hostname -i)
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
hostnm=$(hostname -s)
hostfnm=$(hostname -f)
eval $(ipcalc -ns $hostip $netmask)
net=$(echo $NETWORK | cut -d. -f1-3)

eval $(awk -F"," '/dhcp-range=/{printf "lrg=%s; hrg=%s; lease=%s",
	 substr($1,12), $2, $3}' $CONF_F)

cat <<-EOF
	<form action=dnsmasq_proc.cgi method=post>
	<fieldset><Legend> $s Dynamically serve IPs $es</legend><table>
	<tr><td> $s From IP $es </td><td><input type=text size=12 name=low_rg value=$lrg></td><tr>
	<tr><td> $s To IP $es </td><td><input type=text size=12 name=high_rg value=$hrg></td><tr>
	<tr><td> $s Lease Time: $es </td><td><input type=text size=4 name=lease value=$lease></td><tr>
	</table></fieldset><br>

	<fieldset><Legend> $s Serve fixed IPs based on MAC $es</legend>
	<table><tr align=center>
	<td> $s Name $es </td><td> $s IP $es </td><td> $s Get MAC $es </td>
	<td> $s MAC $es </td><td> $s Lease $es </td></tr>
EOF

oifs="$IFS"; IFS=","; cnt=0
while read mac nm ip lease rest; do
    if test -z "$mac" -o ${mac#\#} != $mac; then continue; fi
    if test "$nm" = "$hostnm"; then continue; fi

    echo "<tr><td><input size=12 type=text name=nm_$cnt value=$nm></td>
	<td><input size=12 type=text name=ip_$cnt value=$ip></td>
	<td><input type=submit name=_$cnt value="Get"></td>
	<td><input size=18 type=text name=mac_$cnt value=$mac></td>
	<td><input size=4 type=text name=lease_$cnt value=$lease></td></tr>"
    cnt=$((cnt+1))
done < $CONF_H

IFS=$oifs
for i in $(seq $cnt $((cnt+2))); do
	echo "<tr><td><input size=12 type=text name=nm_$i></td>
		<td><input size=12 type=text name=ip_$i></td>
		<td><input type=submit name=_$i value="Get"></td>
		<td><input size=17 type=text name=mac_$i></td>
		<td><input size=4 type=text name=lease_$i></td></tr>"
done

cat <<-EOF
	</table></fieldset><br>
	<input type=hidden name=cnt_din value="$i">

	<fieldset><legend> $s Local hosts with fixed IP $es </legend><table>
	<tr align=center><td> $s Name $es </td><td> $s IP $es </td></tr>
EOF

cnt=0
while read ip fname nm; do
	if test -z "$ip" -o ${ip#\#} != $ip -o \
		"$fname" = "localhost" -o "$nm" = "localhost" ; then continue; fi
	#if $(grep -q ",${nm}," $CONF_H); then continue; fi
	
	mac=""; lease=""
	echo "<tr><td><input size=12 type=text name=knm_$cnt value=$nm></td>
		<td><input size=12 type=text name=kip_$cnt value=$ip></td></tr>"
	cnt=$((cnt+1))
done < $HOSTS

for i in $(seq $cnt $((cnt+2))); do
	echo "<tr><td><input size=12 type=text name=knm_$i></td>
		<td><input size=12 type=text name=kip_$i></td></tr>"
done

cat <<EOF
	</table></fieldset>
	<input type=hidden name=cnt_know value="$i">
EOF

echo "<br><fieldset><legend> $s Forward DNS Servers $es </legend>"

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

echo "</fieldset><br><fieldset><legend> $s Time Servers $es </legend>"
i=0
if test -e $CONFNTP; then
	while read server host; do
		if test "$server" = "server" -a "$host" != "127.127.1.0"; then
			echo "Server $((i+1)) <input type=text readonly size=12 name=ntp_$i value=$host><br>"
			i=$((i+1))
		fi
	done < $CONFNTP
fi

echo "<input type=hidden name=cnt_ntp value="$i"></fieldset><br>"

eval $(awk -F= '/enable-tftp/{print "tftp=CHECKED"} \
		/tftp-root/{printf "tftproot=%s", $2}' $CONF_F)

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
	<fieldset><legend> $s TFTP server $es </legend>
	<table>
	<tr><td>Enable TFTP</td><td><input type=checkbox $tftp value=tftp name=tftp></td><tr>
	<tr><td>Root Directory</td>
		<td><input id=tftproot type=text size=20 name=tftproot value=$tftproot>
		<input type=button onclick="browse_dir_popup('tftproot')" value=Browse>
		</td></tr>
	</table></fieldset><br>
EOF

eval $(awk '/log-queries/{print "dnslog=CHECKED"} \
		/log-dhcp/{print "dhcplog=CHECKED"}' $CONF_F)

cat<<EOF	
	<fieldset><legend> $s Logging $es </legend><table>
	<tr><td>Log DNS queries</td>
		<td><input type=checkbox $dnslog name=dnslog value=true></td></tr>
	<tr><td>Log DHCP queries</td>
		<td><input type=checkbox $dhcplog name=dhcplog value=true></td></tr>
	</table></fieldset>
	<input type=hidden name=cnt_dns value="$i">
	<input type=submit name=submit value=Submit>
	<input type=button name=back value="Back" onclick="history.back()">
	</form></body></html>
EOF
