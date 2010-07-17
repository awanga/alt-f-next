#!/bin/sh

. common.sh
check_cookie

write_header "miniDLNA Setup"

CONFF=/etc/minidlna.conf

if test -e $CONFF; then
	MDLNA_DIR="$(awk -F= '/^media_dir/{printf "%s;", $2}' $CONFF)" 
fi

cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
			start_dir = document.getElementById(input_id).value;
			if (start_dir == "")
				start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
	</script>

	<form name=minidlna action=minidlna_proc.cgi method="post" >
	<table><tr>
EOF

OIFS="$IFS"; IFS=";"; k=1
for i in $MDLNA_DIR; do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id=conf_dir_$k name=sdir_$k value="$i"></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$k')" value=Browse></td>
		</tr>
	EOF
    k=$((k+1))
done
IFS="$OIFS"

for j in $(seq $k $((k+2))); do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id=conf_dir_$j name=sdir_$j value=""></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$j')" value=Browse></td>
		</tr>
	EOF
done

cat<<-EOF
	<tr><td></td><td>
	<input type=hidden name=cnt value=$j>
	<input type=submit value=Submit> $(back_button)
	</td></tr></table></form></body></html>
EOF
