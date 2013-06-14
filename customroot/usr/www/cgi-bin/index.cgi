#!/bin/sh

. common.sh

fill_menu() {
	echo -e "<div id=\"$1\" class=\"Menu\">$1</div>\n<div id=\"$1_sub\">"
	awk -F: '{printf("<a class=\"Menu\" href=\"%s\" target=\"content\">%s</a>\n", $2, $1)}' $1.men
	echo "</div><script type=\"text/javascript\">MenuEntry(\"$1\");</script>"
}

if test -n "$QUERY_STRING"; then		
	parse_qstring
	pg="$(httpd -d "$pg")"
fi

echo -e "Content-Type: text/html; charset=UTF-8\r\n\r"

cat<<-EOF
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
	<html><head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<style type="text/css">
		body { font-family: arial,verdana;}
	</style>
	$(load_thm default.thm)	
	<title>Index</title></head><body>
EOF

echo "<table cellspacing=0><tr>"
shortcuts_fill
awk -F: '/<hr>/{while(getline) printf("<a href=\"%s\" target=\"content\">%s</a><br>", $2, $1)}' Shortcuts.men

cat<<EOF
	<div class="Menu">Menu</div>
	<a href="/cgi-bin/logout.cgi" target="content">Logout</a><br>
	<a href="/cgi-bin/status.cgi" target="content">Status</a><br>
EOF

for i in $(cat Main.men); do
	echo "<a href=\"/cgi-bin/index.cgi?pg=$i\">$i</a><br>"
	if test "$i" = "$pg"; then
		awk -F: '{printf("&emsp;<a href=\"%s\" target=\"content\">%s</a><br>", $2, $1)}' $i*.men
	fi
done

for i in Setup Disk Services Packages System; do
	fill_menu $i
done

echo "</body></html>"
