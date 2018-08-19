#!/bin/sh

. common.sh
check_cookie

write_header "MediaTomb Setup"

CONFF=/var/lib/mediatomb/config.xml

eval $(awk '/<ui enabled=/{print substr($2,1,length($2))}' $CONFF)
if test "$enabled" = "yes"; then
	chkweb="checked"
fi

webbut="enabled"
rcmediatomb status >& /dev/null
if test $? != 0 -o "$chkweb" != "checked"; then
		webbut="disabled"
fi

sname="$(sed -n 's|.*<name>\(.*\)</name>|\1|p' $CONFF)"

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

	<form name=mediatomb action=mediatomb_proc.cgi method="post" >
	<table>
	<tr><th>Share Folder</th><th></th></tr>
EOF

OIFS=$IFS; IFS=: ; k=1
for i in $(awk -F\" '/<directory /{printf "%s:", $2}' $CONFF); do
	cat<<-EOF
		<td><input type=text size=32 id="conf_dir_$k" name="sdir_$k" value="$i"></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$k')" value=Browse></td>
		</tr>
	EOF
    k=$((k+1))
done
IFS=$OIFS

for j in $(seq $k $((k+2))); do
	cat<<-EOF
		<td><input type=text size=32 id="conf_dir_$j" name="sdir_$j" value=""></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$j')" value=Browse></td>
		</tr>
	EOF
done

cat<<-EOF
	</table><p><table>
	<tr><td>Server Name</td><td><input type=text name=sname value="$sname"></td></tr>
	<tr><td>Enable Web</td><td><input type=checkbox id=chkweb $chkweb name="ENABLE_WEB" value="yes" onclick="edisable('chkweb','webbut', '$webbut')"></td></tr>
	</table>
	<input type=hidden name=cnt value=$j>
	<p><input type=submit value=Submit> $(back_button)
	<input type="submit" id=webbut $webbut name="webPage" value="WebPage">
	</form></body></html>
EOF
