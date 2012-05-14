#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/sabnzbd/sabnzbd.conf

PORT=$(awk '/[misc]/{ while (st = getline) { if ($1 == "port") {print $3; exit}}}' $CONFF)
PROTO="http"

if echo $HTTP_REFERER | grep -q 'https://'; then
	if grep -q '^enable_https.*=.*1' $CONF	; then
		PORT=$(sed -n '/^https_port/s/.*= *\([0-9]*\)/\1/p' $CONFF)
		PROTO="https"
	fi
fi

if ! rcsabnzbd status >& /dev/null; then
	rcsabnzbd start >& /dev/null
fi

embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT"
