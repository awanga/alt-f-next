#!/bin/sh

. common.sh
check_cookie
write_header "HTTP server Setup"

CONFF=/etc/httpd.conf

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
network=$(echo $hostip | awk -F. '{printf "%d.%d.%d.", $1,$2,$3}')

OIFS="$IFS"
IFS=:
while read tk ip; do
	if test "$tk" = "A"; then
		remip="$(eatspaces $ip | cut -d "#" -f 1)"
		if test "$remip" != "127.0.0.1" -a "$remip" != "$network"; then break; fi
		remip=""
	fi
done < $CONFF
IFS="$OIFS"

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


