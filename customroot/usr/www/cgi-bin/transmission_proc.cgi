#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/var/lib/transmission
JSON=settings.json
SMBCONF=/etc/samba/smb.conf

TRANSMISSION_USER=transmission
TRANSMISSION_GROUP=network

#debug

if test -n "$WebPage"; then
	embed_page "http://$(hostname -i | tr -d ' '):9091"
fi

if test -z "$WATCH_DIR"; then
	msg "You must specify the directory where to Download."
fi

WATCH_DIR="$(httpd -d $WATCH_DIR)"
INCOMPLETE_DIR="$WATCH_DIR/InProgress"
DOWNLOAD_DIR="$WATCH_DIR/Finished"

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
	SEED_RATIO=2
fi

if test -z "$SEED_LIMIT_ENABLED"; then
	SEED_LIMIT_ENABLED=false
	SEED_LIMIT=30
fi

if test -z "$BLOCKLIST_ENABLED"; then
	BLOCKLIST_ENABLED=false
	BLOCKLIST_URL="http://www.bluetack.co.uk/config/level1.gz"
else
	BLOCKLIST_URL=$(httpd -d $BLOCKLIST_URL)
fi

sed -i -e 's|.*"download-dir":.*|    "download-dir": "'$DOWNLOAD_DIR'",|' \
	-e 's|.*"incomplete-dir":.*|    "incomplete-dir": "'$INCOMPLETE_DIR'",|' \
	-e 's|.*"watch-dir":.*|    "watch-dir": "'$WATCH_DIR'",|' \
	-e 's|.*"rpc-enabled":.*|    "rpc-enabled": '$ENABLE_WEB',|' \
	-e 's|.*"ratio-limit-enabled":.*|    "ratio-limit-enabled": '$SEED_RATIO_ENABLED',|' \
	-e 's|.*"ratio-limit":.*|    "ratio-limit": '$SEED_RATIO',|' \
	-e 's|.*"idle-seeding-limit-enabled":.*|    "idle-seeding-limit-enabled": '$SEED_LIMIT_ENABLED',|' \
	-e 's|.*"idle-seeding-limit":.*|    "idle-seeding-limit": '$SEED_LIMIT',|' \
	-e 's|.*"blocklist-enabled":.*|    "blocklist-enabled": '$BLOCKLIST_ENABLED',|' \
	-e 's|.*"blocklist-url":.*|    "blocklist-url": "'$BLOCKLIST_URL'",|' \
	"$CONFF/$JSON"

chown $TRANSMISSION_USER:$TRANSMISSION_GROUP "$CONFF/$JSON"

if ! grep -q "^\[Transmission\]" $SMBCONF; then
	cat<<-EOF >> $SMBCONF

		[Transmission]
		comment = Transmission Download area
		path = "$WATCH_DIR"
		public = yes
		read only = no
		available = yes
	EOF

	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi
fi

if rctransmission status >& /dev/null; then
	rctransmission reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

