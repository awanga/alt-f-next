#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/transmission.conf

#debug

echo "CONF_DIR=$(httpd -d $CONF_DIR)
DOWNLOAD_DIR=$(httpd -d $DOWNLOAD_DIR)
WATCH_DIR=$(httpd -d $WATCH_DIR)" > $CONFF

#rctransmission status
#if test $? = 0; then
#	rctransmission restart
#fi

#enddebug
gotopage /cgi-bin/transmission.cgi

