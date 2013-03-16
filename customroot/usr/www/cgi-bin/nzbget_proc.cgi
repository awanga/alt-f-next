#!/bin/sh

. common.sh
check_cookie
read_args

#debug

NZBCONF=/etc/nzbget.conf
NZBWDATA=/opt/nzbgetweb
NZBWCONF=$NZBWDATA/settings.php
NZBWCONFT=$NZBWDATA/settings-template.php

CONF_LIGHTY=/etc/lighttpd/lighttpd.conf
CONF_LIGHTY2=/etc/lighttpd/modules.conf
CONF_SSL=/etc/lighttpd/conf.d/ssl.conf
PHP_CONF=/etc/php.ini

SMBCF=/etc/samba/smb.conf

nzbgw() {
	if test -f $NZBWCONF; then
		NZBT=$NZBWCONF
	elif test -f $NZBWCONFT; then
		NZBT=$NZBWCONFT
	fi

	if test -n "$NZBT"; then
		sed -i -e "s|^\$NzbDir=.*|\$NzbDir='$1/nzb';|" \
			-e "s|^\$CheckSpaceDir.*|\$CheckSpaceDir='$conf_dir';|" $NZBT
	fi
}

if test -f "$NZBWCONFT" -a ! -f "$NZBWCONF"; then # first time install

	sroot=$(sed -n 's|^var.server_root.*=.*"\(.*\)"|\1|p' $CONF_LIGHTY)
	if test "$(basename $sroot)" = "Public"; then
		msg "You have to configure lighttpd first"
	fi

	rm -f "$sroot"/htdocs/nzbgetweb
	ln -sf $NZBWDATA "$sroot"/htdocs/nzbgetweb

	# nzbgetweb, through php/lighttpd needs to be able to write nzbget.conf file
	addgroup lighttpd TV
	chown -R lighttpd:network $NZBWDATA
	chown nzbget:TV /etc/nzbget*
	chmod g+w /etc/nzbget*
	
	# setup php modules
	for i in json session; do
		sed -i "s|^;extension="$i".so|extension="$i".so|" $PHP_CONF
	done

	#enable php
	sed -i 's|.*\(include.*fastcgi.conf.*\)|\1|' $CONF_LIGHTY2

	if rclighttpd status >& /dev/null; then
   	    rclighttpd restart >& /dev/null
	fi
fi

if test -n "$submit"; then

	if test -n "$conf_dir"; then
		conf_dir=$(httpd -d $conf_dir)
	fi

	if test "$(basename $conf_dir)" = "Public"; then
		msg "You must create a folder for NZBget." 
	elif ! res=$(check_folder "$conf_dir"); then
		msg "$res"
	fi

	if rcnzbget status >& /dev/null; then
		nzbworking=yes
		rcnzbget stop >& /dev/null
		while rcnzbget status >& /dev/null; do
			usleep 200000
		done
	fi
		
	sed -i 's|^$MAINDIR=.*|$MAINDIR='"$conf_dir"'|' $NZBCONF
	nzbgw "$conf_dir"

	chown -R nzbget:TV "$conf_dir"
	chmod g+rwxs "$conf_dir"

	if ! grep -q '\[NZBget\]' $SMBCF; then
		cat <<EOF >> $SMBCF

[NZBget]
	comment = NZBget download area
	path = $conf_dir
	valid users = +TV
	available = yes
	read only = yes
EOF
	else
		sed -i "/\[NZBget\]/,/\[.*\]/ { s|path.*|path = $conf_dir|}" $SMBCF
	fi
	
	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi

	if test -n "$nzbworking"; then
		rcnzbget start >& /dev/null
	fi

elif test -n "$webPage"; then

	nzbgw "$(sed -n 's|^$MAINDIR=\(.*\)|\1|p' $NZBCONF)"

	PROTO="http"
	PORT=$(grep ^server.port $CONF_LIGHTY | cut -d" " -f3)
	
	if echo $HTTP_REFERER | grep -q 'https://'; then
		if grep -q '^include.*ssl.conf' $CONF_LIGHTY; then
			PROTO="https"
			PORT=$(sed -n 's/$SERVER\["socket"\] == ":\(.*\)".*/\1/p' $CONF_SSL)
		fi
	fi

	embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT/nzbgetweb" "NZBget Page"
fi

gotopage /cgi-bin/user_services.cgi
