#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

check_cookie
write_header "Dynamic DNS Setup"
check_https

CONFF=/etc/inadyn.conf

mktt tt_host "Registered hostname.<br>freedns.afraid.org now don't accept hash and accepts username and password."

sites="dyndns@dyndns.org default@zoneedit.com default@no-ip.com default@freedns.afraid.org
default@easydns.com dyndns@3322.org default@sitelutions.com default@dnsomatic.com ipv6tb@he.net
default@tzo.com default@dynsip.org default@dhis.org default@majimoto.net default@zerigo.com default@two-dns.de default@dnsdynamic.org default@dnspark.com ipv4@regfish.de ipv6@regfish.de default@ovh.com default@joker.com default@strato.com default@system-ns.com default@dtdns.com default@changeip.com default@dnsexit.com ipv4@nsupdate.info ipv6@nsupdate.info default@loopia.com default@duckdns.org default@dy.fi"

verbose=0

if test -f $CONFF; then
	while read -r key value; do
		if test -n "$key" -a -n "$value" -a "${key###}" = "$key"; then
			if test "$key" = "password"; then
				password=$(httpd -e "$value")
			else
				eval "$key=$value"
			fi
		fi
	done < $CONFF

	#freedns.afraid.org now only accepts username and password, remove hash
	if echo $alias | grep -q ','; then
		alias=$(echo $alias | sed -n 's/,.*$//p')
	fi

	if test "$verbose" -gt "3"; then
		verbose_chk=checked
	fi
fi

options="<option>Select one</option>"

for i in $sites; do
	site=$(echo $i | cut -d"@" -f2)
	sel=""
	if test "$dyndns_system" = $i; then sel=selected; fi
	options="$options <option $sel>$site</option>"
done

cat<<-EOF
	<form name="formd" action="/cgi-bin/ddns_proc.cgi" method="post">

	<table><tr>
		<td> provider:</td>
		<td><select name="provider">
		$options
		</select></td></tr>
	<tr><td><div id=host_id>hostname:</div></td>
		<td><input type="text" value="$alias" name="host" $(ttip tt_host)></td></tr>
	<tr><td>username:</td>
		<td><input type="text" value="$username" name="user"></td></tr>
	<tr><td>password:</td>
		<td><input type="password" value="$password" name="passwd"></td></tr>
	<tr><td>verbose log:</td>
		<td><input type="checkbox" $verbose_chk name="verbose" value="yes"></td></tr>
	</table>
	<p><input type="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
