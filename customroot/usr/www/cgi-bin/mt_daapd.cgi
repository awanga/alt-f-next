#!/bin/sh

. common.sh
check_cookie
read_args

write_header "mt-daapd Setup"

CONFF=/etc/mt-daapd.conf
DEF_DIR=/var/lib/mt-daapd/mp3_dir

MP3_DIR="$(awk '/^mp3_dir/{print substr($0, index($0,$2))}' $CONFF)"

OIFS="$IFS"; IFS=";"
if test "$MP3_DIR" = "$DEF_DIR"; then
	def_dir=yes
	MP3_DIR=""
	for i in $(ls $DEF_DIR | tr '\n' ';'); do
		if test -z "$i"; then continue; fi
		MP3_DIR="$(readlink $DEF_DIR/$i),$MP3_DIR"
	done
fi
IFS="$OIFS"

rcmt_daapd status >& /dev/null
if test $? != 0; then
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
	</script>

	<form name=transmission action=mt_daapd_proc.cgi method="post" >
	<table>
EOF

OIFS="$IFS"; IFS=','; k=1
for i in $MP3_DIR; do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id="conf_dir_$k" name="sdir_$k" value="$i"></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$k')" value=Browse></td>
		</tr>
	EOF
    k=$((k+1))
done
IFS="$OIFS"

if test "$def_dir" = "yes"; then
for j in $(seq $k $((k+2))); do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id="conf_dir_$j" name="sdir_$j" value=""></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$j')" value=Browse></td>
		</tr>
	EOF
done
fi

cat<<-EOF
	<tr><td></td><td>
	<input type=hidden name=cnt value=$j>
	<input type=hidden name=def_dir value=$def_dir>
	<input type=submit value=Submit> $(back_button)
	<input type="submit" id=webbut $webbut name="webPage" value="WebPage">
	</td></tr></table></form></body></html>
EOF
