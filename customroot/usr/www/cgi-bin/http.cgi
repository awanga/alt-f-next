#!/bin/sh

. common.sh
check_cookie
write_header "HTTP server Setup"

CONFF=/etc/httpd.conf

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK

remip=$(sed -n "s|^A:\(.*\)#!# Allow remote.*$|\1|p" $CONFF)

cat<<-EOF
	<form id="httpf" action="/cgi-bin/http_proc.cgi" method="post">
	<table>
	<tr><td>Remote Administration IP:</td><td><input type=text name="remip" value="$remip"></td></tr>
	<tr><td></td><td><input type="submit" value="Submit">$(back_button)</td></tr>
	</table>
	<input type=hidden name=oldremip value="$remip">
	</form>
	</body></html>
EOF


