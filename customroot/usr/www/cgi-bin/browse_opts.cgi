#!/bin/sh

. common.sh
check_cookie
write_header "Select Options"

if test -n "$QUERY_STRING"; then		
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')
else
	echo "<script type="text/javascript"> window.close() </script></body></html>"
	exit 0
fi

echo "<pre>$(set)</pre>"

opts="auto,defaults,users,user,ro,rw"
case $kind in
	nfs_mnt_opt)
		opts="sync,async,soft,hard,intr,nointr,lock,nolock,
			auto,defaults,users,user,ro,rw"
	;;
esac

cat <<-EOF
	<script type="text/javascript">
		function ret_val(id) {
			var x=document.getElementById("bopt");
			ret="";
			for (i=0; i<x.length; i++) {
				if (x.options[i].selected == true)
					ret += x.options[i].text + ",";	
			}
			window.opener.document.getElementById(id).value = ret;
			window.close();
		}
	</script>
	<form><select id=bopt multiple>
EOF

#awk -F',' -v opts=$opts 'BEGIN{
echo $opts | awk -F',' -v eopts="$eopts" 'BEGIN {
	split(eopts, enab, ",") }
	{
	for (i=1; i<=NF; i++) {
		sel="" 
		for (o in enab) {
			if (enab[o] == $i) {
				sel="SELECTED"
				break
			}
		}
		printf "<option %s>%s</option>", sel, $i
		}
	}'

cat <<-EOF
	</select>
	<input type=submit value=OK onclick="ret_val('$id')">
	<input type=submit value=Cancel onclick=window.close()>
	</form></body></html>
EOF

exit 0
