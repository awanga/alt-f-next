#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

check_cookie
write_header "Dynamic DNS Setup"
check_https

CONFF=/etc/inadyn.conf

mktt tt_host "Registered hostname.<br>For freedns.afraid.org, use \"host,hash\"<br>
where "hash" is everything after the ? in the Direct URL."

cat<<EOF
	<script type="text/javascript">
	function val() {
		idx = document.formd.provider.selectedIndex
		prov = document.formd.provider.options[idx].value
		if (prov == "freedns.afraid.org") {
			document.formd.user.disabled = true;
			document.formd.passwd.disabled = true;
			document.getElementById("host_id").innerHTML = 
'hostname,<a href="http://freedns.afraid.org/dynamic/" target="_blank">Direct URL<\/a>'
		} else {
			document.formd.user.disabled = false;
			document.formd.passwd.disabled = false;
			document.getElementById("host_id").innerHTML = "hostname:"
		}
	}
	</script>
EOF

sites="dyndns@dyndns.org default@zoneedit.com default@no-ip.com default@freedns.afraid.org
default@easydns.com dyndns@3322.org default@sitelutions.com default@dnsomatic.com ipv6tb@he.net
default@tzo.com default@dynsip.org default@dhis.org default@majimoto.net default@zerigo.com"

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
fi

options="<option>Select one</option>"

for i in $sites; do
	site=$(echo $i | cut -d"@" -f2)
	sel=""
	if test "$dyndns_system" = $i; then sel=selected; fi
	if test "$site" = "freedns.afraid.org"; then updis=disabled; fi
	options="$options <option $sel>$site</option>"
done

cat<<-EOF
	<form name="formd" action="/cgi-bin/ddns_proc.cgi" method="post">

	<table><tr>
		<td> provider:</td>
		<td><select name="provider" onchange="val()">
		$options
		</select></td></tr>
	<tr><td><div id=host_id>hostname:</div></td>
		<td><input type="text" value="$alias" name="host" $(ttip tt_host)></td></tr>
	<tr><td>username:</td>
		<td><input type="text" $updis value="$username" name="user"></td></tr>
	<tr><td>password:</td>
		<td><input type="password" $updis value="$password" name="passwd"></td></tr>
	</table>
	<p><input type="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
