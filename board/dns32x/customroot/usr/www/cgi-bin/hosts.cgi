#!/bin/sh

. common.sh
check_cookie
write_header "Fixed IP Hosts Setup"

CONF_HOSTS=/etc/hosts

cat<<-EOF
	<form name=hosts action=hosts_proc.cgi method=post>
	<table><tr><th>Name</th><th>IP</th></tr>
EOF

cnt=0
while read ip fname nm; do
	if test -z "$ip" -o "${ip#\#}" != "$ip" -o \
		"$fname" = "localhost" -o "$nm" = "localhost" ; then continue; fi

	#if echo "$ip" | grep -q ':'; then
		if test -z "$nm" -a -n "$fname"; then nm=$fname; fname=""; fi
	#fi
	
	mac=""; lease=""
	echo "<tr><td><input size=12 type=text name=knm_$cnt value=$nm></td>
		<td><input size=12 type=text name=kip_$cnt value=$ip></td></tr>"
	cnt=$((cnt+1))
done < $CONF_HOSTS

for i in $(seq $cnt $((cnt+2))); do
	echo "<tr><td><input size=12 type=text name=knm_$i></td>
		<td><input size=12 type=text name=kip_$i></td></tr>"
done

cat <<EOF
	</table>
	<p><input type=hidden name=cnt_know value="$i">
	<input type=submit name=submit value=Submit>
	</form></body></html>
EOF
