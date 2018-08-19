#!/bin/sh

. common.sh
check_cookie
write_header "inetd Setup"

CONFF=/etc/inetd.conf

#debug

cat<<-EOF
	<form action="/cgi-bin/inetd_proc.cgi" method="post">
	<table><tr>
	<th>Service</th>
	<th>Program</th>
	<th class="highcol">Enable</th>
	<th></th><th>Description</th>
	</tr>
EOF

i=1
while read srv tp nt wt ow exep exe args; do
	#echo $srv:$tp:$nt:$wt:$ow:$exep:exe:$args:$args1
	if test -z "$srv" -o -z "$tp" -o -z "$nt" -o -z "$wt" -o \
		-z "$ow" -o -z "$exep" -o -z "$exe"; then
		continue
	fi

	desc="<td></td>"
	if echo $args | grep -q '#'; then
		desc="<td>${args##*#}</td>"
	fi

	chkf="checked"
	if test "${srv:0:1}" = "#"; then
		srv=${srv:1}
		chkf=""
	fi
	
	disf="";
	if test -f $PWD/${srv}.cgi; then
		conf="<td><input type="submit" name=$srv value="Configure"></td>"
		disf="disabled"
	else
		conf="<td></td>"
	fi

	cat<<-EOF
		<tr><td>$srv</td><td><em>$exe</em></td>
		<td class="highcol">
		<input type=checkbox $chkf name=chk_$i value=enable>
		<input type=hidden name=srv_$i value=$srv>
		<input type=hidden name=prog_$i value=$exe>
		</td>
		$conf $desc
		</tr>
	EOF
	i=$((i+1))
done < $CONFF

cat<<-EOF
	<tr><td></td><td></td>
	<td class="highcol">
	<input type=hidden name=cnt value=$i>
	<input type="submit" name=submit value="Submit"></td><td>$(back_button)</td>	
	</tr></table></form></body></html>
EOF

#enddebug

