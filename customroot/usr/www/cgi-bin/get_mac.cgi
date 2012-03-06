#!/bin/sh

. common.sh
check_cookie

html_header

#debug

if test -n "$QUERY_STRING"; then		
	parse_qstring
else
	echo "<script type="text/javascript"> window.close() </script></body></html>"
	exit 0
fi

	ip=$(eval echo \$ip$Get)

	if test -z "$ip"; then
		echo "<p>You must supply an host ip to get its MAC</p>"
	elif ! checkip $ip; then
		echo "<p>The IP must be in the form x.x.x.x, where x is greater than 0 and less then 255</p>"
	else
		echo "<p>Getting MAC of host with IP $ip...</p>"
		ping -W 3 -c 2 $ip >/dev/null 2>&1
		if test $? = 1; then
			echo "<p>Host is not answering, can't get its MAC.</p>"
		else
			res=$(arp -n $ip)
			if test "$(echo $res | cut -d" " -f1,2,3)" = "No match found"; then
				echo "<p>Host is alive but couldn't get its MAC.</p>"
			else
				lease=$(eval echo \$lease_$GetMAC)
				mac=$(echo $res | cut -d" " -f 4)
				cat<<-EOF
					<script type="text/javascript">
						window.opener.document.getElementById("$id").value = "$mac";
						window.close()
					</script></body></html>
				EOF
				exit 0
			fi
		fi
	fi

echo "<input type=button value=\"OK\" onclick=\"window.close()\"></body></html>"
