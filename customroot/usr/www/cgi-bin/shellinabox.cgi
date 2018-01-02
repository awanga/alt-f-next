#!/bin/sh

. common.sh
check_cookie
read_args

if ! rcshellinabox status >& /dev/null; then
	rcshellinabox start >& /dev/null
fi

CONFF=/etc/shellinabox.conf

if test -s $CONFF; then . $CONFF; fi

embed_page "https://${HTTP_HOST%%:*}:${PORT:-4200}" "Shell in a box Page"
