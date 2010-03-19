#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

check_cookie
write_header "Dynamic DNS Setup"

CONFF=/etc/inadyn.conf
SSCRIPT=/etc/init.d/S75ddns

if test -f $CONFF; then
	while read line; do
		eval $(echo $line | awk '!/#/{if (NF == 2) print $1 "=" $2}')
	done < $CONFF

	case $dyndns_system in
		dyndns@dyndns.org) ddns=dyndns.org ;;	
		default@zoneedit.com) ddns=zoneedit.com ;;
		default@no-ip.com) ddns=no-ip.com ;;
		default@freedns.afraid.org) ddns=freedns.afraid.org ;;
	esac
else
	ddns="Select one"
	alias=""
	username=""
	password=""
fi

cat<<-EOF
    <form action="/cgi-bin/ddns_proc.cgi" method="post">

    <table><tr>
        <td> provider:</td>
        <td><select name="provider">
                <option selected> $ddns
		<option> dyndns.org
		<option> freedns.afraid.org
                <option> zoneedit.com
                <option> no-ip.com
        </select></td></tr>
    <tr>
        <td>hostname:</td>
        <td><input type="text" value="$alias" name="host" ></td>
    </tr>
    <tr>
        <td>username:</td>
        <td><input type="text" value="$username" name="user"></td>
    </tr>
    <tr>
        <td>password:</td>
        <td><input type="password" value="$password" name="passwd"></td>
    </tr>

	<tr><td></td><td><input type="submit" value="submit">
	<input type=button name=back value="Back" onclick="history.back()"></tr>
    </table></form></body></html>
EOF

