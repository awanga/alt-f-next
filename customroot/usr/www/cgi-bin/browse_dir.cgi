#!/bin/sh

. common.sh
check_cookie
write_header "Directory Browse Window"

#echo "<pre>$(set)</pre>"
#echo QUERY_STRING=$QUERY_STRING

if test -n "$QUERY_STRING"; then	
	
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')

	browse="$(httpd -d "$browse")"

	echo "$browse" | grep -q '^/mnt'
	if test "$?" = 1; then
		echo "<h3>Warning: Directory base must be /mnt</h3>"
		browse="/mnt"
	elif ! test -d "$browse"; then
		echo "<h3>Warning: Directory \"$browse\" does not exist.</h3>"
		browse="/mnt"
	fi

	cat <<-EOF
		<script type="text/javascript">
			function ret_val(inp, adir) {
				window.opener.document.getElementById(inp).value = adir;
				window.close();
			}
		</script>

		<form action=/cgi-bin/create_dir.cgi method=post><table><tr>
		<td>Current directory:</td>
		<td><input type=text READONLY value="$browse"></td>
		<td><input type=submit value=OK onclick="ret_val('$id', '$browse')"></td>
		<td><input type=submit value=Cancel onclick=window.close()></td>
		</tr>
	EOF

	cat<<-EOF
		<tr><td>Create directory:</td>
		<td><input type=text name=newdir value="$browse"></td>
		<td colspan="2"><input type=submit value=CreateDir></td><td></td>
		</tr></table></form>

		<ul style='list-style-type:none'>
		<li><a href="/cgi-bin/browse_dir.cgi?id=$id?browse=$(dirname "$browse")">
			<strong>Up directory</strong></a></li>
	EOF

	# FIXME spaces in file name
	# a=$(find "$browse" -maxdepth 1 -type d -a ! -name '.*' -a ! -name "$bn")
	a=$(find "$browse" -maxdepth 1 -type d -a ! -name '.*' |  tr '\n' ':')
	IFS=':'
	for i in $a; do
		echo "<li><a href=\"/cgi-bin/browse_dir.cgi?id=$id?browse=$i\">$i</a></li>"
	done
	IFS=' '
	echo "</ul>"

fi
echo "</body></html>"
exit 0
