#!/bin/sh

. common.sh
check_cookie
read_args

TCONF=/var/lib/amule/amule.conf
SMBCONF=/etc/samba/smb.conf

AMULE_USER=amule
AMULE_GROUP=BT

#debug

if test -n "$WebPage"; then
	if ! rcamule status >& /dev/null; then
		rcamule start  >& /dev/null
	fi
	port=$(sed -n '/\[WebServer\]/,/\[/{s|^Port=\(.*\)|\1|p}' $TCONF)	
	embed_page "http://${HTTP_HOST%%:*}:${port}" "aMule Page"

elif test -n "$Submit"; then

	if test -n "$DL_DIR"; then
		DL_DIR=$(httpd -d "$DL_DIR")
	fi

	if test "$(basename $DL_DIR)" = "Public"; then
		msg "You must create a folder for aMule." 
	elif ! res=$(check_folder "$DL_DIR"); then
		msg "$res"
	fi

	chown -R $AMULE_USER:$AMULE_GROUP "$DL_DIR"
	chmod -R g+rws "$DL_DIR"

	sed -i -e "s|^TempDir=.*|TempDir=$DL_DIR/Temp|" \
		-e "s|^IncomingDir=.*|IncomingDir=$DL_DIR/Incoming|" $TCONF

	chown $AMULE_USER:$AMULE_GROUP "$TCONF"

	if ! grep -q "^\[aMule\]" $SMBCONF; then
		cat<<EOF >> $SMBCONF

[aMule]
	comment = aMule Download area
	path = $DL_DIR
	valid users = +BT
	read only = no
	available = yes
EOF
	else
		sed -i "/\[aMule\]/,/\[.*\]/ { s|path.*|path = $DL_DIR|}" $SMBCONF
	fi

	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi

	if rcamule status >& /dev/null; then
		rcamule reload >& /dev/null
	fi

	#enddebug
	gotopage /cgi-bin/user_services.cgi
fi
