#!/bin/sh

. common.sh
check_cookie
write_header "ffp Setup"

if ! test -f /ffp/etc/rc; then
	echo "No ffp installation found<br>$(back_button)</body></html>"
	exit 0
fi

cat<<-EOF
	<h4 class="warn">You must <strong>NOT</strong> enable services that might conflict with Alt-F services, and services have to be manually configured.</h4>
	<form action="/cgi-bin/ffp_proc.cgi" method="post">
	<table><tr>
	<th>Service</th>
	<th>Enable</th><th>Status</th>
	<th></th>
	</tr>
EOF

cnt=1
for srv in $(ls /ffp/start/*.sh); do
	nm=$(basename $srv .sh)
	chkf=""; if test -x $srv; then chkf=checked; fi
	res=$(PATH=/ffp/bin:/ffp/sbin:$PATH /ffp/bin/sh $srv status 2>&1)

	st=""
	if echo $res | grep -q 'not.*running'; then
		st="Stopped"
	elif echo $res | grep -q 'running'; then
		st="<strong>Running</strong>"
	fi

	cat<<-EOF
		<tr><td>$nm</td>
		<td align=center><input type=checkbox $chkf name=ffp_$cnt value=$srv></td><td>$st</td>
		$conf
		</tr>
	EOF
	cnt=$((cnt+1))
done

cat<<-EOF
	</table>
	<p><input type="submit" name=submit value="Submit">$(back_button)
	<input type=hidden name=cnt value=$cnt>
	</form></body></html>
EOF
