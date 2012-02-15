#!/bin/sh

. common.sh
check_cookie
write_header "HTTP server Setup"

CONFF=/etc/httpd.conf

mktt rem_tt "All hosts from the local network are already allowed<br>
to access the administrative web pages.<br><br>

Specify, if needed, an external IP address that you wish to also<br>
have access to the administrative web pages.<br>
Remember that passwords are transmited in plaintext, you are<br>
advised to install the 'stunnel' package and use secure http.<br><br>

The IP must be in the form x.x.x.x, x.x.x.x/y.y.y.y, or x.x.x.x/n,<br> 
where x or y is between 1 and 254 and n can be 8, 16, 24, 32."

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK

cat<<-EOF
	<form id="httpf" action="/cgi-bin/http_proc.cgi" method="post">
	<table>
	<tr><th>Disable</th><th>Allowed Remote Administration IPs</th></tr>
EOF

cnt=1
for i in $(sed -n "s|A:\(.*\)#!# Allow remote.*$|\1|p" $CONFF); do
	dis=""
	if test ${i:0:1} = "#"; then
		dis=checked
		i=${i:1}
	fi

	echo "<tr><td align=center><input type=checkbox $dis name=dis_$cnt></td>
	<td><input type=text name=remip_$cnt value=\"$i\" $(ttip rem_tt)></td></tr>"
	cnt=$((cnt+1))
done

for j in $(seq $cnt $((cnt+2))); do
	echo "<tr><td align=center><input type=checkbox name=dis_$j></td>
	<td><input type=text name=remip_$j value=\"\" $(ttip rem_tt)></td></tr>"
	j=$((j+1))
done

cat<<-EOF
	<tr><td></td><td><input type="submit" value="Submit">$(back_button)</td></tr>
	</table>
	<input type=hidden name=oldremip value="$remip">
	<input type=hidden name=httpd_cnt value="$j">
	</form>
	</body></html>
EOF


