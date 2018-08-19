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
	<fieldset><legend>RSS Feeds</legend>
	<table>
	<tr><th>Feed URL</th><th>Private Cookie</th></tr>
EOF

TF=$(mktemp)
cnt=0
sed -n '/^feed/Ns/.*url.*"\(.*\)".*cookie.*"\(.*\)".*/feed="\1";cookie="\2"/p' $CONF_AUTO > $TF
while read i; do
	eval $i
	cat<<-EOF
		<tr><td><input type=text size=40 name="feed_$cnt" value="$feed"></td>
		<td><input type=text size=20 name="cookie_$cnt" value="$cookie"></td></tr>
	EOF
	cnt=$((cnt+1))
done < $TF

for i in $(seq $cnt $((cnt+2))); do
	cat<<-EOF
		<tr><td><input type=text size=40 name="feed_$i" value=""></td>
		<td><input type=text size=20 name="cookie_$i" value=""></td></tr>
	EOF
done

cat<<EOF
	</table></fieldset>
	<input type=hidden name=feed_cnt value="$i">
	<fieldset><legend>Download Patterns</legend>
	<table>
	<tr><th>Pattern</th><th>Download to Folder</th><th></th></tr>
EOF

cnt=0
sed -n '/^filter/Ns/.*pattern.*"\(.*\)".*folder.*"\(.*\)".*/pattern="\1";folder="\2"/p' $CONF_AUTO > $TF
while read i; do
	eval $i
	echo "
		<tr><td><input type=text size=40 name=\"pattern_$cnt\" value=\"$pattern\"></td>
		<td><input type=text size=20 id=\"folder_$cnt\" name=\"folder_$cnt\" value=\"$folder\"></td>
		<td><input type=button value=Browse onclick=\"browse_dir_popup('folder_$cnt')\"></td></tr>
	"
	cnt=$((cnt+1))
done < $TF

rm $TF

for i in $(seq $cnt $((cnt+2))); do
	cat<<-EOF
		<tr><td><input type=text size=40 name="pattern_$i" value=""></td>
		<td><input type=text size=20 id="folder_$i" name="folder_$i" value=""></td>
		<td><input type=button value=Browse onclick="browse_dir_popup('folder_$i')"></td></tr>
	EOF
done

eval $(awk '/^interval/ { printf "interval=%d;", $3 }
	/^start-torrents/ { if ($3 == "yes") printf "start_chk=\"checked\";"
	}' $CONF_AUTO)

cat <<EOF
	</table></fieldset>
	<input type=hidden name=pattern_cnt value="$i">
	<table>
	<tr><td>Start downloading new torrents automatically
	<input type=checkbox $start_chk name=start_downloads value=yes></td></tr>
	<tr><td>Check for new downloads every
	<input type=text size=3 name=interval value="$interval">min</td></tr>
	</table><br>

	<input type=submit name=submit value=Submit>$(back_button)
	</form></body></html>
EOF
