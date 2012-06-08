#!/bin/sh

. common.sh
check_cookie

eval $(echo -n $QUERY_STRING | tr '\r' '\n' | sed -e 's/'"'"'/%27/g' | \
	awk 'BEGIN{RS="&";FS="="}
		$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')

#debug

if test -z "$add" -a -z "$rm"; then
	gotopage $(basename $url _proc.cgi).cgi

elif test -n "$add"; then
	title=$(httpd -d $add)
	if ! grep -q "$title" bookmarks.html; then
		echo "<a href=\"$url\" target=\"content\">$title</a><br>" >> bookmarks.html
	fi

	html_header
	cat<<-EOF
		<script type="text/javascript">
			parent.nav.location.reload()
			location.assign("/cgi-bin/$(basename $HTTP_REFERER)")
		</script>
	EOF

elif test -n "$rm"; then
	title=$(httpd -d $rm)
	if test -n "$title"; then
		sed -i "\|$title|d" bookmarks.html
	fi

	html_header
	cat<<-EOF
		<script type="text/javascript">
		parent.frames.nav.location.assign("/cgi-bin/index.cgi")
		parent.frames.content.location.assign("$url")
		</script>
	EOF
fi

echo "</body></html>"
