#!/bin/sh

if test -n "$QUERY_STRING"; then		
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')

	pg="$(httpd -d "$pg")"
fi

cat<<-EOF
	Content-Type: text/html; charset=UTF-8

	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
	<html><head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	</head><body>
	<script type="text/javascript">
		function addbookmark() {
			location.assign("/cgi-bin/bookmark.cgi?add=" + parent.content.document.title +
				 "&url=" + parent.content.window.location.pathname)
		}
		function rmbookmark() {
			location.assign("/cgi-bin/bookmark.cgi?rm=" + parent.content.document.title +
				 "&url=" + parent.content.window.location.pathname)
		}
	</script>
EOF

if test -s bookmarks.html; then
	echo "<h4>Bookmarks</h4>"
	cat bookmarks.html
	echo "<button type=button onClick=\"rmbookmark()\">Remove Current</button><h4>Menu</h4>"
fi

cat<<EOF
	<a href="/cgi-bin/logout.cgi" target="content">Logout</a><br>
	<a href="/cgi-bin/status.cgi" target="content">Status</a><br>
EOF

for i in Setup Disk Services Packages System; do
	echo "<a href=\"/cgi-bin/index.cgi?pg=$i\">$i</a><br>"
	IFS=" "
	if test "$i" = "$pg"; then
		extra=$(cat $i*.men)
		echo $extra | while read entry url; do
			echo "&emsp;<a href=\"/cgi-bin/$url\" target=\"content\">$entry</a><br>"
		done
	fi
done

#echo "<a href=\"/cgi-bin/bookmark.cgi\" onClick=\"addbookmark()\">Bookmark</a><br>"
echo "<button type=button onClick=\"addbookmark()\">Bookmark</button>"

echo "</body></html>"
