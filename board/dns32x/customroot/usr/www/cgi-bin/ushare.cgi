#!/bin/sh

. common.sh
check_cookie

write_header "uShare Setup"

CONF_USHARE=/etc/ushare.conf

mktt dlna_tt "Some devices might require this. A full rescan will be needed each time the server starts."

if test -e $CONF_USHARE; then
	USHARE_DIR="$(awk -F= '/^USHARE_DIR/{print $2}' $CONF_USHARE)" 
	USHARE_NAME="$(awk -F= '/^USHARE_NAME/{print $2}' $CONF_USHARE)"
	eval $(grep ^USHARE_ENABLE_ /etc/ushare.conf | sed 's/yes/checked/')
fi

webbut="enabled"
rcushare status >& /dev/null
if test $? != 0 -o "$USHARE_ENABLE_WEB" != "checked"; then
		webbut="disabled"
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
		function edisable(chk, but, st) {
			if (st == "disabled")
				return;
			if (document.getElementById(chk).checked == true)
				document.getElementById(but).disabled = false;
			else
				document.getElementById(but).disabled = true;
		}
	</script>

	<form name=transmission action=ushare_proc.cgi method="post" >
	<table>
EOF

OIFS="$IFS"; IFS=','; k=1
for i in $USHARE_DIR; do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id="conf_dir_$k" name="sdir_$k" value="$i"></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$k')" value=Browse></td>
		</tr>
	EOF
    k=$((k+1))
done
IFS="$OIFS"

for j in $(seq $k $((k+2))); do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id="conf_dir_$j" name="sdir_$j" value=""></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$j')" value=Browse></td>
		</tr>
	EOF
done

cat<<-EOF
	<tr><td>&emsp;</td></tr>
	<tr><td>Server Name</td><td><input type=text name=sname value="$USHARE_NAME"></td></tr>
	<tr><td>Enable DLNA</td><td><input type=checkbox $USHARE_ENABLE_DLNA name="USHARE_ENABLE_DLNA" value="yes" $(ttip dlna_tt)></td></tr>
	<tr><td>Enable XboX</td><td><input type=checkbox $USHARE_ENABLE_XBOX name="USHARE_ENABLE_XBOX" value="yes"></td></tr>
	<tr><td>Enable Web</td><td><input type=checkbox id=chkweb $USHARE_ENABLE_WEB name="USHARE_ENABLE_WEB" value="yes" onclick="edisable('chkweb','webbut', '$webbut')"></td></tr>
	<tr><td></td><td>
	<input type=hidden name=cnt value=$j>
	<input type=submit value=Submit> $(back_button)
	<input type="submit" id=webbut $webbut name="webPage" value="WebPage">
	</td></tr></table></form></body></html>
EOF
