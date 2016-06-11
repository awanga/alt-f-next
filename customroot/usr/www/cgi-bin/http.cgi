#!/bin/sh

. common.sh
check_cookie
write_header "Administrative HTTP/HTTPS servers Setup"

CONFF=/etc/httpd.conf
INETD_CONF=/etc/inetd.conf

mktt rem_tt "All hosts from the local network are already allowed to access <br>
the administrative web pages.<br><br>
Specify an external network or IP address (no validity checks done)<br>
allowed to have http access to the administrative web pages.<br>
Or use instead secure https, where all hosts are already allowed.<br><br>
Even with https the Alt-F webUI might have security vulnerabilities and<br>
it is not recommended to expose it to the internet."

mktt port_tt "The default HTTP port is 80, so you can access the webUI using<br>
\"http://&lt;box-ip&gt;\" or \"http://&lt;box-ip&gt;:80\".<br><br>
If you want to use that port for other purposes select the alternate 8080 port<br>
and use \"http://&lt;box-ip&gt;:8080\" to access the webUI."

mktt sport_tt "The default HTTPS port is 443, so you can securely access the webUI using<br>
\"https://&lt;box-ip&gt;\" or \"https://&lt;box-ip&gt;:443\".<br><br>
If you want to use that port for other purposes select the alternate 8443 port<br>
and use \"https://&lt;box-ip&gt;:8443\" to access the webUI."

mktt inetd_tt "Inetd mode: runs only when necessary, slower to start, conserves memory."
mktt server_tt "Server mode: always running, faster, always consuming memory<br>
(the corresponding checkboxes in the inetd web page will be unchecked)."

if grep -q http_alt $INETD_CONF; then
	ALT_PORT_CHK="checked"
	OPORT="8080"
	if checkport 80; then
		port_msg="Port 80 currently in use"
		DEF_PORT_DIS="disabled"
	fi
else
	DEF_PORT_CHK="checked"
	OPORT="80"
	if checkport 8080; then
		port_msg="Port 8080 currently in use"
		ALT_PORT_DIS="disabled"
	fi
fi

if grep -q https_alt $INETD_CONF; then
	ALT_SPORT_CHK="checked"
	OSPORT="8443"
	if checkport 443; then
		sport_msg="Port 443 currently in use"
		DEF_SPORT_DIS="disabled"
	fi
else
	DEF_SPORT_CHK="checked"
	OSPORT="443"
	if checkport 8443; then
		sport_msg="Port 8443 currently in use"
		ALT_SPORT_DIS="disabled"
	fi
fi

if grep -qE '(^https|^swats)' $INETD_CONF; then
	STUNNEL_INETD=checked
	OSTUNNEL="inetd"
else
	STUNNEL_SERVER=checked
	OSTUNNEL="server"
fi

if grep -qE '(^http|^http_alt)[[:space:]]*.*httpd' $INETD_CONF; then
	HTTPD_INETD=checked
	OHTTPD="inetd"
else
	HTTPD_SERVER=checked
	OHTTPD="server"
fi

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK

cat<<-EOF
	<h4 class="warn">After changing the current ports or service mode and Submiting,<br>
	the connection might become broken and you might have to<br>
	reload the page or edit the browser URL accordingly.</h4>
	<form id="httpf" action="/cgi-bin/http_proc.cgi" method="post">
	<fieldset><legend>Administrative HTTP server</legend>
	<table><tr><th>Disable</th><th>Allowed Remote IPs</th></tr>
EOF

cnt=1
for i in $(sed -n "s|A:\(.*\)#!# Allow remote.*$|\1|p" $CONFF); do
	dis=""
	if test ${i:0:1} = "#"; then
		dis=checked
		i=${i:1}
	fi

	cat<<-EOF
		<tr><td align=center><input type=checkbox $dis name=dis_$cnt></td>
		<td><input type=text name=remip_$cnt value="$i" $(ttip rem_tt)></td></tr>
	EOF
	cnt=$((cnt+1))
done

for j in $(seq $cnt $((cnt+2))); do
	cat<<-EOF
		<tr><td align=center><input type=checkbox name=dis_$j></td>
		<td><input type=text name=remip_$j value="" $(ttip rem_tt)></td></tr>
	EOF
	j=$((j+1))
done

cat<<-EOF
	</table>
	<table>
	<tr><td></td></tr>
	<tr><td>Listen on port:</td>
		<td align=right>80<input type=radio $DEF_PORT_DIS $DEF_PORT_CHK name=port value="80" $(ttip port_tt)></td>
		<td></td>
		<td>8080<input type=radio $ALT_PORT_DIS $ALT_PORT_CHK name=port value="8080" $(ttip port_tt)></td>
		<td>$port_msg</td></tr>
	</table>
	<table>
		<tr><td></td></tr>
		<tr><td>inetd mode</td><td><input type=radio $HTTPD_INETD name=httpd value="inetd" $(ttip inetd_tt)></td></tr>
		<tr><td>server mode</td><td><input type=radio $HTTPD_SERVER name=httpd value="server" $(ttip server_tt)></td></tr>
	</table>
	</fieldset>

	<fieldset><legend>Secure Administrative HTTPS server</legend>
	<table>
	<tr><td>Listen on port:</td>
		<td align=right>443<input type=radio $DEF_SPORT_DIS $DEF_SPORT_CHK name=sport value="443" $(ttip sport_tt)></td>
		<td></td>
		<td>8443<input type=radio $ALT_SPORT_DIS $ALT_SPORT_CHK name=sport value="8443" $(ttip sport_tt)></td>
		<td>$sport_msg</td></tr>
	</table>
	<table>
		<tr><td></td></tr>
		<tr><td>inetd mode</td><td><input type=radio $STUNNEL_INETD name=stunnel value="inetd" $(ttip inetd_tt)></td></tr>
		<tr><td>server mode</td><td><input type=radio $STUNNEL_SERVER name=stunnel value="server" $(ttip server_tt)></td></tr>
	</table>
	</fieldset>

	<p><input type="submit" value="Submit">$(back_button)
	<input type="hidden" name=ohttpd value="$OHTTPD">
	<input type="hidden" name=oport value="$OPORT">
	<input type="hidden" name=ostunnel value="$OSTUNNEL">
	<input type="hidden" name=osport value="$OSPORT">
	<input type="hidden" name=from_url value="$HTTP_REFERER">
	<input type=hidden name=oldremip value="$remip">
	<input type=hidden name=httpd_cnt value="$j">
	</form>
	</body></html>
EOF


