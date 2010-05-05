#!/bin/sh

. common.sh
check_cookie
write_header "inetd Setup"

CONFF=/etc/inetd.conf

#debug
	
s="<strong>"
es="</strong>"


cat<<-EOF
	<form action="/cgi-bin/inetd_proc.cgi" method="post">
	<table><tr>
	<td> $s Service $es </td>
	<td> $s Enable $es </td>
	<td></td>
	</tr>
EOF

	# FIXME: add service description
	ssrv="rsync ssh telnet ftp http printer swat"
	for i in $ssrv; do
		chkf=""
		if $(grep -q -e "^$i" $CONFF); then
			chkf="CHECKED"
		fi
		
		cat<<-EOF
			<tr><td> $i </td>
			<td align=center><input type=checkbox $chkf name=$i value=enable></td>
			<td><input type="submit" name=$i value="Configure"></td>
			</tr>
		EOF
	done


cat<<-EOF
	<tr><td><input type="submit" name="$ssrv" value="Submit"></td>
	<td><input type=button name=back value="Back" onclick="history.back()"></td></tr>
	</table></form></body></html>
EOF

#enddebug

