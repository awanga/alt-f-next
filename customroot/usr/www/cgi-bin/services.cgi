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

cat<<-EOF
	<script type="text/javascript">
	function toogle(theform) {
		for (var i = 0; i < theform.length; i++) {
			if (theform.elements[i].id == "inetds")
				theform.elements[i].disabled = theform.elements[i].disabled ? false : true;
		}
	}
	</script>

	<form name=srvf action="/cgi-bin/services_proc.cgi" method="post">
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
		st="Running"
		act="StopNow"
	else
		st="Stopped"
		act="StartNow"
	fi

	script=""
	if test "$i" = "inetd"; then
		script="onchange=\"toogle(srvf)\""
	fi

	cat<<-EOF
		<tr><td> $i </td>
		<td align=center><input type=checkbox $chkf name=$i value=enable $script></td>
		<td>$st</td>
		<td><input type="submit" name=$i value="$act"></td>
		<td><input type="submit" name=$i value="Configure"></td>
		<td>$DESC</td></tr>
	EOF
done

# FIXME: add description
if test $action = "net"; then

	inetdf=""
	if ! test -x /etc/init.d/S??inetd; then
		inetdf="disabled"
	fi

	ssrv="rsync ssh telnet ftp http printer swat"
	for i in $ssrv; do
		chkf=""
		if $(grep -q -e "^$i" $CONFF); then
			chkf="CHECKED"
		fi
		
		cat<<-EOF
			<tr><td><em>&emsp; $i </em></td>
			<td align=center><input type=checkbox $inetdf id=inetds $chkf name=$i value=enable></td>
			<td></td><td></td>
			<td><input type="submit" $inetdf id=inetds name=$i value="Configure"></td></tr>
		EOF
	done
	echo "<tr><td><input type=hidden name=\"$ssrv\" value=SSubmit></td></tr>"
fi

cat<<-EOF
	<tr><td></td>
	<td><input type="submit" name="$srv" value="Submit"></td></tr>
	</table></form></body></html>
EOF

#enddebug
