#!/bin/sh

. common.sh
check_cookie

if test -n "$QUERY_STRING"; then		
	parse_qstring
else
	write_header "NFS options error"
	echo "<script type="text/javascript"> window.close() </script></body></html>"
	exit 0
fi

#debug

case $kind in
	nfs_mnt_opt)
		opts="proto=,sync,async,soft,hard,intr,nointr,lock,nolock,noauto,defaults,users,user,rw,ro"
		title="NFS mount options"
		;;
	nfs_exp_opt)
		opts="ro,rw,sync,async,nohide,no_subtree_check,crossmnt,mountpoint,fsid=,
			root_squash,no_root_squash,all_squash,anonuid=,anongid="
		title="NFS export options"
		;;
esac

html_header "$title"

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
	<form><select id="bopt" multiple size="15" style="width: 20em">
EOF

# FIXME manage options of kind var=val
echo $opts | awk -F',' -v eopts="$eopts" '
	BEGIN { split(eopts, enab, ",") }
	{
	for (i=1; i<=NF; i++) {
		sel=""
		show=$i
		for (j in enab) {
			if (index(enab[j], $i) == 1) {
				sel="selected"
				show=enab[j]
				break
			}
		}
		printf "<option %s>%s</option>\n", sel, show
		}
	}'

cat <<-EOF
	</select><br>
	<input type=submit value=OK onclick="ret_val('$id')">
	<input type=submit value=Cancel onclick=window.close()>
	</form></body></html>
EOF

exit 0
