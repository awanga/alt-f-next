#!/bin/sh

. common.sh
check_cookie

if test -n "$QUERY_STRING"; then
	parse_qstring
fi

embed_page "$(httpd -d $site)" "$name"
