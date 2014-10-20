#!/bin/sh

. common.sh
check_cookie
read_args

if ! rcnut status >& /dev/null; then
	rcnut start >& /dev/null
fi

PROTO="http"
if echo $HTTP_REFERER | grep -q 'https://'; then
	PROTO="https"
fi

embed_page "$PROTO://${HTTP_HOST%%:*}/nut" "NUT Page"
