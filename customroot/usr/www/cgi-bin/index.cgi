#!/bin/sh

. common.sh

if test -n "$QUERY_STRING"; then		
	parse_qstring
	pg="$(httpd -d "$pg")"
fi

echo -e "Content-Type: text/html; charset=UTF-8\r\n\r"

cat<<-EOF
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
	<html><head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<script type="text/javascript">
	$(cat base.js)
	</script>
	<style type="text/css">
	$(cat base.css)
	body { font-family: arial,verdana;}
	</style>
	<title>Index</title></head><body>
EOF

if test -s bookmarks.html; then
	echo "<table cellspacing=0><tr>"
	bookmark_fill
	cat bookmarks.html
fi

cat<<EOF
	<div class="Menu">Menu</div>
	<a href="/cgi-bin/logout.cgi" target="content">Logout</a><br>
	<a href="/cgi-bin/status.cgi" target="content">Status</a><br>
EOF

for i in Setup Disk Services Packages System; do
	echo "<a href=\"/cgi-bin/index.cgi?pg=$i\">$i</a><br>"
	if test "$i" = "$pg"; then
		extra=$(cat $i*.men)
		echo "$extra" | while read entry url; do
			echo "&emsp;<a href=\"/cgi-bin/$url\" target=\"content\">$entry</a><br>"
		done
	fi
done

echo "</body></html>"
