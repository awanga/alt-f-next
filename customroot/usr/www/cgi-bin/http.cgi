#!/bin/sh

. common.sh
check_cookie
write_header "Administrative HTTP server Setup"

CONFF=/etc/httpd.conf
INETD_CONF=/etc/inetd.conf

mktt rem_tt "All hosts from the local network are already allowed<br>
to access the administrative web pages.<br><br>

Specify, if needed, an external IP address that you wish to also<br>
have http access to the administrative web pages.<br>
Remember that passwords are transmited in plaintext, you are<br>
advised to use https (FIXME: where all IPs are already allowed).<br><br>

The IP must be in the form x.x.x.x, x.x.x.x/y.y.y.y, or x.x.x.x/n,<br> 
where x or y is between 1 and 254 and n can be 8, 16, 24, 32."

mktt port_tt "The default http port is 80, which means that you can access your box
adminstrative web pages<br>
 using the URL \"http://&lt;box-ip&gt;\" or \"http://&lt;box-ip&gt;:80\".<br>
For https, the default is to use port 443, meaning that you can use<br>
\"https://&lt;box-ip&gt;\" or \"https://&lt;box-ip&gt;:443\".<br><br>
If you want to use alternative ports, because, e.g., you want to run the lighttpd server on the
default ports,<br>
you can here select different ports for the administrative web server,<br>
and using \"http://&lt;box-ip&gt;:8080\" or \"https://&lt;box-ip&gt;:8443\" to access it."

mktt stunneli_tt "Inetd mode: stunnel runs only when necessary, slower to start, conserves memory."

mktt stunnels_tt "Server mode: stunnel always running, faster, always consuming memory<br>
(the https/swats checkboxes in the inetd web page will be unchecked)."

if grep -q http_alt $INETD_CONF; then
	ALT_PORT_CHK="checked"
	if checkport 80; then
		port_msg="Port 80 currently in use"
		DEF_PORT_DIS="disabled"
	fi
else
	DEF_PORT_CHK="checked"
	if checkport 8080; then
		port_msg="Port 8080 currently in use"
		ALT_PORT_DIS="disabled"
	fi
fi

if grep -q https_alt $INETD_CONF; then
	ALT_SPORT_CHK="checked"
	if checkport 443; then
		sport_msg="Port 443 currently in use"
		DEF_SPORT_DIS="disabled"
	fi
else
	DEF_SPORT_CHK="checked"
	if checkport 8443; then
		sport_msg="Port 8443 currently in use"
		ALT_SPORT_DIS="disabled"
	fi
fi

if grep -qE '(^https|^swats)' $INETD_CONF; then
	STUNNEL_INETD=checked
else
	STUNNEL_SERVER=checked
fi

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK

cat<<-EOF
	<form id="httpf" action="/cgi-bin/http_proc.cgi" method="post">
	<fieldset><legend>Ports</legend>
	<table><tr><th></th><th>Default</th><th>&emsp;</th><th>Alternative</th></tr>
	<tr><td><strong>http:</strong></td>
		<td align=right>80<input type=radio $DEF_PORT_DIS $DEF_PORT_CHK name=port value="80" $(ttip port_tt)></td>
		<td></td>
		<td>8080<input type=radio $ALT_PORT_DIS $ALT_PORT_CHK name=port value="8080" $(ttip port_tt)></td>
		<td>$port_msg</td></tr>
	<tr><td><strong>https:</strong></td>
		<td align=right>443<input type=radio $DEF_SPORT_DIS $DEF_SPORT_CHK name=sport value="443" $(ttip port_tt)></td>
		<td></td>
		<td>8443<input type=radio $ALT_SPORT_DIS $ALT_SPORT_CHK name=sport value="8443" $(ttip port_tt)></td>
		<td>$sport_msg</td></tr>
	</table></fieldset>

	<fieldset><legend>The stunnel program provides https and can be run in</legend>
	<table>
		<tr><td>inetd mode</td><td><input type=radio $STUNNEL_INETD name=stunnel value="inetd" $(ttip stunneli_tt)></td></tr>
		<tr><td>server mode</td><td><input type=radio $STUNNEL_SERVER name=stunnel value="server" $(ttip stunnels_tt)></td></tr>
	</table>
	</fieldset>

	<fieldset><legend>Remote Administration</legend>
	<table><tr><th>Disable</th><th>Allowed IPs</th></tr>
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
	</table></fieldset>
	<p><input type="submit" value="Submit">$(back_button)
	<input type=hidden name=oldremip value="$remip">
	<input type=hidden name=httpd_cnt value="$j">
	</form>
	</body></html>
EOF


