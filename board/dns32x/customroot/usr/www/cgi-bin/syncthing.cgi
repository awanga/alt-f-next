#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/var/lib/syncthing/config.xml

if ! rcsyncthing status >& /dev/null; then
	rcsyncthing start >& /dev/null
fi

PROTO="http"
if echo $HTTP_REFERER | grep -q 'https://'; then
    PROTO="https"
fi

PORT=$(sed -n 's|.*<address>.*:\([[:digit:]]*\)</address>|\1|p' $CONFF)

embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT" "Syncthing Page"
