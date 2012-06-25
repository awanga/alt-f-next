#!/bin/sh

. common.sh
check_cookie
read_args

if ! rccups status >& /dev/null; then
	rccups start >& /dev/null
fi

PROTO="http"
if echo $HTTP_REFERER | grep -q 'https://'; then
	PROTO="https"
fi

embed_page "$PROTO://${HTTP_HOST%%:*}:631/admin" "CUPS Page"
