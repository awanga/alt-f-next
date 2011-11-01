#!/bin/sh

. common.sh
check_cookie

eval $(echo -n $QUERY_STRING | tr '\r' '\n' | sed -e 's/'"'"'/%27/g' | \
	awk 'BEGIN{RS="&";FS="="}
		$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')

#debug

html_header

if test -n "$add"; then
	title=$(httpd -d $add)

	if ! grep -q "$title" bookmarks.html; then
		echo "<a href=\"$url\" target=\"content\">$title</a><br>" >> bookmarks.html
	fi

	cat<<-EOF
		<script type="text/javascript">
			parent.nav.location.reload()
			location.assign("/cgi-bin/$(basename $HTTP_REFERER)")
		</script>
	EOF


elif test -n "$rm"; then
	title=$(httpd -d $rm)
	sed -i "\|$title|d" bookmarks.html

	cat<<-EOF
		<script type="text/javascript">
		location.assign("/cgi-bin/index.cgi")
		</script>
	EOF
fi

echo "</body></html>"
