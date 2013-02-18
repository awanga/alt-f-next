#!/bin/sh

. common.sh
check_cookie

html_header "NFS Browse"

if test -n "$QUERY_STRING"; then		
	parse_qstring
else
	echo "<h3>No arguments given.</h3></body></html>"
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

wait_count_start "Browsing the network for NFS servers, it takes 20 seconds"

# this seems to be needed to start the window drawn...
for i in $(seq 1 20); do sleep 1; echo; done &

echo "<br><br><strong>Host:Folder</strong><br>"

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

wait_count_stop

echo "<br><form action=\"\"><input type=submit onclick=\"window.close()\" value=Cancel>
		</form></body></html>"
