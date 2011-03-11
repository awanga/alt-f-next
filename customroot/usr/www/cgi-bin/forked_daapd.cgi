#!/bin/sh

. common.sh
check_cookie
read_args

write_header "forked-daapd Setup"

CONF_FORKED=/etc/forked-daapd.conf

SHARE_DIRS=$(awk -F= '/directories/{print $2}' $CONF_FORKED | tr -d '{}')

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

	<form name=forked action=forked_daapd_proc.cgi method="post" >
	<table><tr>
EOF

OIFS="$IFS"; IFS=','; k=1
for i in $SHARE_DIRS; do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id="sdir_$k" name="sdir_$k" value=$i></td>
		<td><input type=button onclick="browse_dir_popup('sdir_$k')" value=Browse></td>
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
