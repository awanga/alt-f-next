#!/bin/sh

. common.sh

if test -s "$CONF_MISC"; then . $CONF_MISC; fi

echo -e "Content-Type: text/html; charset=UTF-8\r\n\r"

cat<<-EOF
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
	<html><head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<head profile="http://www.w3.org/2005/10/profile">
	<link rel="icon" type="image/png" href="../dns-323.png"/>
	$(load_thm default.thm)
	$(menu_setup "side" "$SIDE_MENU")
	<title>Index</title>
	</head><body>
	</body></html>
EOF
