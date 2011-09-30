#!/bin/sh

. common.sh
check_cookie
write_header "ssh server Setup"

#debug

CONF_INETD=/etc/inetd.conf

eval $(awk '/(^ssh|#ssh)/{ if ($6 == "/usr/sbin/dropbear") {
	if (index($8,"s")) print "NOPASS_CHK=checked; "
	if (index($8,"w")) print "NOROOT_CHK=checked; "
	if (index($8,"g")) print "NOROOTPASS_CHK=checked; "
	print "dropbear=yes"
	} else	print "dropbear=no"
}' $CONF_INETD)

if test "$dropbear" != "yes"; then
	echo "<p>Currently only dropbear is configurable</p> $(back_button) </body></html>"
	exit 0
fi

#if ipkg info openssh | grep -q not-installed; then
#	pkg=dropbear
#else
#	pkg=openssh
#fi

cat<<-EOF
	<form name="ssh" action="/cgi-bin/ssh_proc.cgi" method="post">
	<h3>Configuring Dropbear</h3>
	<table>
	<tr><td>Disable password logins</td><td><input type=checkbox $NOPASS_CHK name=nopass value=yes></td></tr>
	<tr><td>Disallow root logins</td><td><input type=checkbox $NOROOT_CHK name=noroot value=yes></td></tr>
	<tr><td>Disable password logins for root</td><td><input type=checkbox $NOROOTPASS_CHK name=norootpass value=yes></td></tr>
	<tr><td></td><td></td></tr>
	<tr><td></td><td><input type="submit" value="Submit">$(back_button)</td></tr>
	</table></form></body></html>
EOF
