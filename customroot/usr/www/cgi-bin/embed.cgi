#!/bin/sh

. common.sh

if test -n "$QUERY_STRING"; then
	parse_qstring
fi

embed_page "$(httpd -d $site)" "$name"
