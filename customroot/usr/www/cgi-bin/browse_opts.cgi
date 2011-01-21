#!/bin/sh

. common.sh
check_cookie

# handle options of kind var=val
if test -n "$QUERY_STRING"; then		
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,substr($0,index($0,"=")+1),39}')
else
	write_header "NFS options error"
	echo "<script type="text/javascript"> window.close() </script></body></html>"
	exit 0
fi

#debug

case $kind in
	nfs_mnt_opt)
		opts="sync,async,soft,hard,intr,nointr,lock,nolock,
			auto,defaults,users,user,ro,rw"
		title="NFS mount options"
		;;
	nfs_exp_opt)
		opts="ro,rw,sync,async,nohide,no_subtree_check,crossmnt,mountpoint,
			fsid=,root_squash,no_root_squash,all_squash,anonuid=,anongid="
		title="NFS export options"
		;;
esac

html_header
echo "<h2><center>$title</center></h2>"

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

# FIXME manage options of kind var=val
echo $opts | awk -F',' -v eopts="$eopts" 'BEGIN {
	split(eopts, enab, ",") }
	{
	for (i=1; i<=NF; i++) {
		sel="" 
		for (o in enab) {
			if (index(enab[o],$i)) {
				sel="SELECTED"
				break
			}
		}
		printf "<option %s>%s</option>", sel, $i
		}
	}'

cat <<-EOF
	</select><br>
	<input type=submit value=OK onclick="ret_val('$id')">
	<input type=submit value=Cancel onclick=window.close()>
	</form></body></html>
EOF

exit 0
