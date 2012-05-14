#!/bin/sh

. common.sh
check_cookie
read_args

CONF=/etc/sickbeard.conf

PORT=$(sed -n '/^web_port/s/.*= *\([0-9]*\)/\1/p' $CONF)

PROTO="http"
if grep -q '^enable_https.*=.*1' $CONF; then
	PROTO="https"
fi

if ! rcsickbeard status >& /dev/null; then
	rcsickbeard start >& /dev/null
fi

embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT"
