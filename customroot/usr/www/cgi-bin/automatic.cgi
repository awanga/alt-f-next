#!/bin/sh

. common.sh
check_cookie
write_header "Automatic Setup"

CONF_AUTO=/etc/automatic.conf

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
	<form name=hosts action=automatic_proc.cgi method=post>
	<fieldset><legend><strong>RSS Feeds</strong></legend>
	<table>
	<tr align=center><th>Feed URL</th><th>Private Cookie</th></tr>
EOF

cnt=0
for i in $(sed -n '/^feed/s/.*url.*"\(.*\)".*cookie.*"\(.*\)".*/feed="\1";cookie="\2"/p' $CONF_AUTO); do
	eval $i
	echo "<tr><td><input type=text size=40 name=feed_$cnt value=$feed></td>
		<td><input type=text size=20 name=cookie_$cnt value=$cookie></td></tr>"
	cnt=$((cnt+1))
done

for i in $(seq $cnt $((cnt+2))); do
	echo "<tr><td><input type=text size=40 name=feed_$i value=""></td>
		<td><input type=text size=20 name=cookie_$i value=""></td></tr>"
done

cat<<EOF
	<input type=hidden name=feed_cnt value="$i">
	</table></fieldset><br>
	<fieldset><legend><strong>Download Patterns</strong></legend>
	<table>
	<tr align=center><th>Pattern</th><th>Download to Folder</th></tr>
EOF

cnt=0
for i in $(sed -n '/^filter/s/.*pattern.*"\(.*\)".*folder.*"\(.*\)".*/pattern="\1";folder="\2"/p' $CONF_AUTO); do
	eval $i
	echo "<tr><td><input type=text size=40 name=pattern_$cnt value=$pattern></td>
		<td><input type=text size=20 id=folder_$cnt name=folder_$cnt value=$folder></td>
		<td><input type=button value=Browse onclick=\"browse_dir_popup('folder_$cnt')\"></td></tr>"
	cnt=$((cnt+1))
done

for i in $(seq $cnt $((cnt+2))); do
	echo "<tr><td><input type=text size=40 name=pattern_$i value=""></td>
		<td><input type=text size=20 id=folder_$cnt name=folder_$i value=""></td>
		<td><input type=button value=Browse onclick=\"browse_dir_popup('folder_$i')\"></td></tr>"
done

eval $(awk '/^interval/ { printf "interval=%d;", $3 }
	/^start-torrents/ { if ($3 == "yes") printf "start_chk=\"checked\";"
	}' $CONF_AUTO)

cat <<EOF
	<input type=hidden name=pattern_cnt value="$i">
	</table></fieldset><br>
	<table>
	<tr><td>Start downloading new torrents automatically
	<input type=checkbox $start_chk name=start_downloads value=yes></td></tr>
	<tr><td>Check for new downloads every
	<input type=text size=3 name=interval value="$interval">min</td></tr>
	</table><br>

	<input type=submit name=submit value=Submit>$(back_button)
	</form></body></html>
EOF
