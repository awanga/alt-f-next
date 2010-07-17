#!/bin/sh

. common.sh
check_cookie
write_header "NFS Browse"

#echo "<pre>$(set)</pre>"

if test -n "$QUERY_STRING"; then		
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')
else
	echo "<script type="text/javascript"> window.close() </script></body></html>"
	exit 0
fi

cat <<-EOF
	<script type="text/javascript">
		function ret_val(id1, host, id2, dir) {
			window.opener.document.getElementById(id1).value = host;
			window.opener.document.getElementById(id2).value = dir;
			window.close();
		}
	</script>
EOF

echo "Browsing network, it takes 30 sec...<br>
	<form><strong>Host:Directory</strong><br>"

rpcinfo -b 100005 3 | sort -u  | while read hip hnm; do
	if test $hnm = "(unknown)"; then
		host=$hip
	else
		host=$hnm
	fi
	showmount -e --no-headers $host	| while read hdir rest; do
		echo "<a href=\"\" onclick=\"ret_val('$id1', '$host', '$id2', '$hdir')\">$host:$hdir</a><br>"
	done
done

echo "<input type=submit onclick=window.close() value=Cancel>
		</form></body></html>"

exit 0
