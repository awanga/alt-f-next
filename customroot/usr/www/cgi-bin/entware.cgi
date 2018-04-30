#!/bin/sh

. common.sh
check_cookie
write_header "Entware Services Setup"

if ! test -f /opt/etc/init.d/rc.unslung; then
	echo "No Entware installation found.<br>$(back_button)</body></html>"
	exit 0
fi

if ! lst=$(ls /opt/etc/init.d/S* 2> /dev/null); then
	echo "No installed services found.<br>$(back_button)</body></html>"
	exit 0
fi

cat<<-EOF
	<h4 class="warn">You must <strong>NOT</strong> enable services that might conflict with Alt-F services and services have to be manually configured.</h4>
	<form action="/cgi-bin/entware_proc.cgi" method="post">
	<table><tr>
	<th>Service</th><th class="highcol">Boot Enabled</th><th>Status</th><th>Action</th>
	<!--th>Description</th-->
	<th></th>
	</tr>
EOF

PATH=$PATH:/opt/bin:/opt/sbin

cnt=1
for srv in $lst; do
	nm=$(basename $srv); nm=${nm:3}
	#desc=$(opkg info $(opkg search $srv | cut -d' ' -f1) | awk '/Description:/{print substr($0,index($0,":")+2)}')

	chkf=""; if test -x $srv; then chkf=checked; fi
	st="Stopped"; act="StartNow"
	if PATH=/opt/bin:/opt/sbin:$PATH sh $srv check >& /dev/null; then
		st="<strong>Running</strong>"; act="StopNow"
	fi

	cat<<-EOF
		<tr><td>$nm</td>
		<td  class="highcol"><input type=checkbox $chkf name=entware_$cnt value=$srv></td><td>$st</td>
		<td><input type="submit" name="$srv" value="$act"></td><td>$desc</td>
		</tr>
	EOF
	cnt=$((cnt+1))
done

cat<<-EOF
	<tr><td></td><td class="highcol"><input type="submit" name="$srv" value="Submit"></td>
	<td colspan=4></td></tr>
	</table>
	$(back_button)<input type=hidden name=cnt value=$cnt>
	</form></body></html>
EOF
