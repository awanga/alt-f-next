#!/bin/sh

. common.sh
check_cookie
read_args

LMSCONF=/etc/lms/server.prefs

if ! rclms status >& /dev/null; then
	rclms start >& /dev/null
fi

while ! test -f $LMSCONF; do sleep 5; done

PORT=$(grep '^httpport:' $LMSCONF  | cut -d" " -f2)

PROTO="http"
if echo $HTTP_REFERER | grep -q 'https://'; then
	PROTO="https"
fi

embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT" "LMS Page"
