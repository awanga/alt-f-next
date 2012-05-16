#!/bin/sh

. common.sh
check_cookie
read_args

CONF=/etc/couchpotato.conf

PORT=$(sed -n '/\[global\]/,/\[.*\]/s/^port.*= *\([0-9]*\)/\1/p' $CONF)
PROTO="http"

if ! rccouchpotato status >& /dev/null; then
	rccouchpotato start >& /dev/null
fi

embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT"
