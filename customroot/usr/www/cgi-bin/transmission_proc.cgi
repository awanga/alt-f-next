#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/var/lib/transmission
JSON=settings.json

TRANSMISSION_USER=transmission
TRANSMISSION_GROUP=network

#debug

if test -n "$WebPage"; then
	embed_page "http://$(hostname -i | tr -d ' '):9091"
fi

if test -z "$DOWNLOAD_DIR" -o -z "$WATCH_DIR" -o -z "$INCOMPLETE_DIR"; then
	msg "You must specify all directories."
fi

INCOMPLETE_DIR="$(httpd -d $INCOMPLETE_DIR)"
DOWNLOAD_DIR="$(httpd -d $DOWNLOAD_DIR)"
WATCH_DIR="$(httpd -d $WATCH_DIR)"

if ! test -d "$DOWNLOAD_DIR" -a -d "$WATCH_DIR" -a -d "$INCOMPLETE_DIR"; then
	mkdir -p "$DOWNLOAD_DIR" "$WATCH_DIR" "$INCOMPLETE_DIR"
fi

chown $TRANSMISSION_USER:$TRANSMISSION_GROUP $DOWNLOAD_DIR $INCOMPLETE_DIR $WATCH_DIR
chmod a+rw $DOWNLOAD_DIR $INCOMPLETE_DIR $WATCH_DIR

if test -z "$ENABLE_WEB"; then
	ENABLE_WEB=false
fi

if test -z "$SEED_RATIO_ENABLED"; then
	SEED_RATIO_ENABLED=false
fi

sed -i -e 's|.*"download-dir":.*|    "download-dir": "'$DOWNLOAD_DIR'",|' \
	-e 's|.*"incomplete-dir":.*|    "incomplete-dir": "'$INCOMPLETE_DIR'",|' \
	-e 's|.*"watch-dir":.*|    "watch-dir": "'$WATCH_DIR'",|' \
	-e 's|.*"rpc-enabled":.*|    "rpc-enabled": '$ENABLE_WEB',|' \
	-e 's|.*"ratio-limit-enabled":.*|    "ratio-limit-enabled": '$SEED_RATIO_ENABLED',|' \
	-e 's|.*"ratio-limit":.*|    "ratio-limit": '$SEED_RATIO',|' \
	"$CONFF/$JSON"

chown $TRANSMISSION_USER:$TRANSMISSION_GROUP "$CONFF/$JSON"

#rctransmission status >& /dev/null
#if test $? = 0; then
	rctransmission reload >& /dev/null
#fi

#enddebug
gotopage /cgi-bin/user_services.cgi

