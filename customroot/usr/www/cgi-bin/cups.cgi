#!/bin/sh

. common.sh
check_cookie
read_args

if ! rccups status >& /dev/null; then
	rccups start >& /dev/null
fi

embed_page "https://${HTTP_HOST%%:*}:631/admin"