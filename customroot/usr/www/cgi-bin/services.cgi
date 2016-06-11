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
		title="Network Services"
		;;
	sys)
		title="System Services"
		;;
	use) # hellas, should be "user"
		title="User Services"
		;;
esac

write_header "$title"

if test -z "$srv"; then
	echo "<center><h4>No services available</h4></center></body></html>"
	exit 0;
fi

cat<<-EOF
	<form action="/cgi-bin/services_proc.cgi" method="post">
	<fieldset>
	<legend>$title</legend>
	<table><tr>
	<th>Service</th>
	<th class="highcol">Boot Enabled</th>
	<th>Status</th>
	<th>Action</th>
	<th></th>
	<th align=left>Description</th></tr>
EOF

for i in $srv; do
	eval $(grep '^DESC=' $CONFD/S??$i)

	chkf=""
	if test -x /etc/init.d/S??$i; then
		chkf="checked"
	fi

	rc$i status >& /dev/null; rst=$?
	if test "$rst" = 0; then
		st="<strong>Running</strong>"
		act="StopNow"
	else
		st="Stopped"
		act="StartNow"
	fi

	ictrl=""
	if test "$rst" = 2; then
		ictrl="disabled"
	fi

	if test -f $PWD/${i}.cgi; then
		NEED_ALTF_DIR=0; dis_wait=""
		eval $(grep '^NEED_ALTF_DIR=' $CONFD/S??$i)
		if test $NEED_ALTF_DIR = 1; then
			if ! aufs.sh -s >& /dev/null; then dis_wait=disabled; fi
		fi
		conf="<td><input $dis_wait type="submit" name=$i value="Configure"></td>"
	else
		conf="<td></td>"
	fi

	cat<<-EOF
		<tr><td> $i </td>
		<td class="highcol"><input type=checkbox $ictrl $chkf name=$i value=enable></td>
		<td>$st</td>
		<td><input type="submit" name=$i value="$act"></td>
		$conf
		<td>$DESC</td></tr>
	EOF
done

cat<<-EOF
	<tr><td></td>
	<td class="highcol"><input type="submit" name="$srv" value="Submit"></td>
	<td colspan=4></td></tr>
	</table></fieldset></form></body></html>
EOF

#enddebug
