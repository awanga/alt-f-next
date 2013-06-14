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
		echo $title:$url >> Shortcuts.men
	fi

	html_header
	cat<<-EOF
		<script type="text/javascript">
			parent.nav.document.location.reload()
			//parent.content.document.location.assign("/cgi-bin/$(basename $HTTP_REFERER)")
			parent.content.document.location.assign("$url")
		</script>
	EOF

elif test -n "$rm"; then

	title=$(httpd -d $rm)
	if test -n "$title"; then
		if test "$title" = "all"; then
			echo -n > bookmarks.html
		else
			sed -i "\|$title|d" bookmarks.html
			sed -i "\|$title|d" Shortcuts.men
		fi
	fi

	html_header
	cat<<-EOF
		<script type="text/javascript">
		parent.nav.document.location.reload()
		parent.content.document.location.assign("$url")
		</script>
	EOF
fi

echo "</body></html>"
