#!/bin/sh

. common.sh
check_cookie
read_args

CONF_WSECRET=/etc/web-secret

if ! rccups status >& /dev/null; then
	rccups start >& /dev/null
fi
pass="$(cat $CONF_WSECRET)"

#embed_page "https://root:${pass}@$(hostname -i | sed 's/ //'):631/admin"
embed_page "https://$(hostname -i | sed 's/ //'):631/admin"

