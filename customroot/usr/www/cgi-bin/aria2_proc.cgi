#!/bin/sh

. common.sh
check_cookie
read_args

CONF=/etc/aria2/aria2.conf
SMBCONF=/etc/samba/smb.conf
CONF_LIGHTY=/etc/lighttpd/lighttpd.conf
CONF_SSL=/etc/lighttpd/conf.d/ssl.conf

ARIA2_USER=aria2
ARIA2_GROUP=BT

#debug

if test -n "$WebPage"; then
	if ! rcaria2 status >& /dev/null; then
		rcaria2 start  >& /dev/null
	fi

	PORT=$(grep ^server.port $CONF_LIGHTY | cut -d" " -f3)
	PROTO="http"
	if echo $HTTP_REFERER | grep -q 'https://'; then
		if grep -q '^include "conf.d/ssl.conf"' $CONF_LIGHTY; then
			PORT=$(sed -n 's/$SERVER\["socket"\] == ":\(.*\)".*/\1/p' $CONF_SSL)
			PROTO="https"
		fi
	fi
	
	embed_page "$PROTO://${HTTP_HOST%%:*}:${PORT}/aria2web" "Aria2 Page"

elif test -n "$Submit"; then

	if test -n "$DL_DIR"; then
		DL_DIR=$(httpd -d "$DL_DIR")
	fi

	if test "$(basename $DL_DIR)" = "Public"; then
		msg "You must create a folder for Aria2." 
	elif ! res=$(check_folder "$DL_DIR"); then
		msg "$res"
	fi

	sed -i "s|^dir=.*|dir=$DL_DIR|" $CONF

	chown -R $ARIA2_USER:$ARIA2_GROUP "$DL_DIR" $CONF
	chmod -R g+rws "$DL_DIR"

	if ! grep -q "^\[Aria2\]" $SMBCONF; then
		cat<<EOF >> $SMBCONF

[Aria2]
	comment = Aria2 Download area
	path = $DL_DIR
	valid users = +BT
	read only = no
	available = yes
EOF

	else
		sed -i "/\[Aria2\]/,/\[.*\]/ { s|path.*|path = $DL_DIR|}" $SMBCONF
	fi

	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi

	if rcaria2 status >& /dev/null; then
		rcaria2 restart >& /dev/null
	fi

	#enddebug
	gotopage /cgi-bin/user_services.cgi
fi
