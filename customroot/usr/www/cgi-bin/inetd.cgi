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
	<th></th>
	</tr>
EOF

# FIXME: add service description
#ssrv=$(awk '{if (substr($1,1,1) == "#") $1=substr($1,2); print $1}' $CONFF)
#for i in $ssrv; do
#	chkf=""
#	if $(grep -q -e "^$i[[:space:]]" $CONFF); then
#		chkf="checked"
#	fi

while read srv tp nt wt ow exep exe args; do
	#echo $srv:$tp:$nt:$wt:$ow:$exep:exe:$args:$args1
	if test -z "$srv" -o -z "$tp" -o -z "$nt" -o -z "$wt" -o \
		-z "$ow" -o -z "$exep" -o -z "$exe"; then
		continue
	fi

	chkf="checked"
	if test "${srv:0:1}" = "#"; then
		srv=${srv:1}
		chkf=""
	fi
	
	if test -f $PWD/${srv}.cgi; then
		conf="<td><input type="submit" name=$srv value="Configure"></td>"
	else
		conf="<td></td>"
	fi

	cat<<-EOF
		<tr><td>$srv</td><td><em>$exe</em></td>
		<td class="highcol"><input type=checkbox $chkf name=$srv value=enable></td>
		$conf
		</tr>
	EOF
done < $CONFF

cat<<-EOF
	<tr><td></td><td></td>
	<td class="highcol"><input type="submit" name=submit value="Submit"></td><td>$(back_button)</td>	
	</tr></table></form></body></html>
EOF

#enddebug

