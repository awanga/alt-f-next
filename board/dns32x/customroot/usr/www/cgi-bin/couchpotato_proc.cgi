#!/bin/sh

. common.sh
check_cookie
read_args

CPCONF=/etc/couchpotato.conf

SABPROG=/opt/SABnzbd/SABnzbd.py
SABCONF=/etc/sabnzbd/sabnzbd.conf

SMBCF=/etc/samba/smb.conf

if test -n "$submit"; then

	if test -n "$conf_dir"; then
		conf_dir=$(httpd -d $conf_dir)
	fi

	if test "$(basename $conf_dir)" = "Public"; then
		msg "You must create a folder for CouchPotato." 
	elif ! res=$(check_folder "$conf_dir"); then
		msg "$res"
	fi

	if rccouchpotato status >& /dev/null; then
		cpworking=yes
		html_header
		busy_cursor_start
		rccouchpotato stop >& /dev/null
		while rccouchpotato status >& /dev/null; do
			usleep 200000
		done
	fi

	if test -f $SABPROG; then # SABnzbd is installed
		if test -z "$(sed -n "/\[Sabnzbd\]/,/\[.*\]/s/^apikey.*=[[:space:]]*\(.*\)/\1/p" $CPCONF)"; then
			sab_apikey=$(sed -n 's/^api_key[[:space:]]*=[[:space:]]*\(.*\)/\1/p' $SABCONF)
			if test -z "$sab_apikey"; then
				sab_apikey=$(uuidgen | tr -d '-')
				sed -i "s/^api_key.*/api_key = $sab_apikey/" $SABCONF
			fi
			sed -i "/\[Sabnzbd\]/,/\[.*\]/s/^apikey.*/apikey = $sab_apikey/" $CPCONF
		fi
	fi

	sed -i "s|^destination.*=.*|destination = $conf_dir|" $CPCONF
	# FIXME: SABdownload, /mnt/md0/SABnzbd/Complete/Movies
	# sed -i "s|^download.*=.*|download = ???|" $CPCONF

	chown -R couchpotato:TV $CPCONF $conf_dir
	chmod g+rwxs $conf_dir

	if ! grep -q '\[CouchPotato\]' $SMBCF; then
		cat <<EOF >> $SMBCF

[CouchPotato]
	comment = CouchPotato download area
	path = $conf_dir
	valid users = +TV
	available = yes
	read only = yes
EOF
	else
		sed -i "/\[CouchPotato\]/,/\[.*\]/ { s|path.*|path = $conf_dir|}" $SMBCF
	fi

	if rcsmbstatus >& /dev/null; then
		rcsmb reload >& /dev/null
	fi

	if test -n "$cpworking"; then
		rccouchpotato start >& /dev/null
		busy_cursor_end
		js_gotopage /cgi-bin/user_services.cgi
	fi

elif test -n "$webPage"; then

	PORT=$(sed -n '/\[global\]/,/\[.*\]/s/^port.*= *\([0-9]*\)/\1/p' $CPCONF)
	PROTO="http"

	embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT" "CouchPotato Page"
fi

gotopage /cgi-bin/user_services.cgi
