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

    <TABLE>
    <TR>
        <TD> Provider:</TD>
        <TD><SELECT NAME="provider">
                <OPTION SELECTED> $ddns
		<OPTION> dyndns.org
		<OPTION> freedns.afraid.org
                <OPTION> zoneedit.com
                <OPTION> no-ip.com
        </SELECT></TD>

    </TR>
    <TR>
        <TD>Hostname:</TD>
        <TD><input type="text" value="$alias" name="host" ></TD>
    </TR>
    <TR>
        <TD>Username:</TD>
        <TD><input type="text" value="$username" name="user"></TD>
    </TR>
    <TR>
        <TD>Password:</TD>
        <TD><input type="password" value="$password" name="passwd"></TD>
    </TR>

    <TR><TD></TD><TD><input type="submit" value="Submit"></TR>

    </TABLE>
    </form>
    </body>
    </html>
EOF

