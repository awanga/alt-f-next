#!/bin/sh

. common.sh
check_cookie

eval $(echo -n $QUERY_STRING | tr '\r' '\n' | sed -e 's/'"'"'/%27/g' | \
	awk 'BEGIN{RS="&";FS="="}
		$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')

url=$(httpd -d $url)

#debug
#exit 0

if test -z "$add" -a -z "$rm"; then
	gotopage $(basename $url _proc.cgi).cgi

elif test -n "$add"; then
	title=$(httpd -d $add)
	if echo "$url" | grep -qE 'https?://'; then
		url="/cgi-bin/embed.cgi?name=$title?site=$(url_encode $url)"
	fi
	if ! grep -q "$title" Shortcuts.men; then
		echo $title\|$url >> Shortcuts.men
	fi

	html_header
	cat<<-EOF
		<script type="text/javascript">
			parent.nav.document.location.reload()
			parent.content.document.location.assign("$url")
		</script>
	EOF

elif test -n "$rm"; then
	title=$(httpd -d $rm)
	if test -n "$title"; then
		if test "$title" = "all"; then
			sed -ni '1,/<hr>/p' Shortcuts.men
		else
			sed -i "\|$title|d" Shortcuts.men
		fi
	fi

	if echo "$url" | grep -qE 'https?://'; then
		url="/cgi-bin/embed.cgi?name=$title?site=$(url_encode $url)"
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
