#!/bin/sh

. common.sh
check_cookie

#debug

CONFD=/etc/init.d/
CONFF=/etc/inetd.conf

pg=$(basename $SCRIPT_NAME)
action=${pg:0:3}

for i in $(ls -r $CONFD); do
	if $(grep -q "^TYPE=$action" $CONFD/$i); then
		srv="$srv ${i:3}" 
	fi
done

case $action in
	net)
		title="Net Services"
		;;
	sys)
		title="System Services"
		;;
	use) # hellas, should be "user"
		title="User Services"
		;;
esac

write_header "$title"
	
s="<strong>"
es="</strong>"

if test -z "$srv"; then
	echo "<center><h4>No services available</h4></center></body></html>"
	exit 0;
fi

cat<<-EOF
	<form action="/cgi-bin/services_proc.cgi" method="post">
	<table><tr>
	<td> $s Service $es </td>
	<td> $s Boot Enabled $es </td>
	<td align=center> $s Status $es </td>
	<td align=center> $s Action $es </td>
	<td></td>
	<td align=center> $s Description $es </td></tr>
EOF

for i in $srv; do
	eval $(grep '^DESC=' $CONFD/S??$i)

	chkf=""
	if test -x /etc/init.d/S??$i; then
		chkf="CHECKED"
	fi

	if rc$i status >/dev/null ; then
		st="$s Running $es"
		act="StopNow"
	else
		st="Stopped"
		act="StartNow"
	fi

	cat<<-EOF
		<tr><td> $i </td>
		<td align=center><input type=checkbox $chkf name=$i value=enable></td>
		<td>$st</td>
		<td><input type="submit" name=$i value="$act"></td>
		<td><input type="submit" name=$i value="Configure"></td>
		<td>$DESC</td></tr>
	EOF
done

cat<<-EOF
	<tr><td></td>
	<td><input type="submit" name="$srv" value="Submit"></td></tr>
	</table></form></body></html>
EOF

#enddebug
