#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/transmission.conf

#debug

if test -z "$CONF_DIR"; then
	msg "You must specify at least the configuration directory"
fi

if test -z "$DOWNLOAD_DIR"; then
	DOWNLOAD_DIR="$CONF_DIR"
fi

if test -z "$WATCH_DIR"; then
	WATCH_DIR="$CONF_DIR"
fi

echo "CONF_DIR=$(httpd -d $CONF_DIR)
DOWNLOAD_DIR=$(httpd -d $DOWNLOAD_DIR)
WATCH_DIR=$(httpd -d $WATCH_DIR)" > $CONFF

rctransmission status >& /dev/null
if test $? = 0; then
	rctransmission restart >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

