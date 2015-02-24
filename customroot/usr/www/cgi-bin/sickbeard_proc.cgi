#!/bin/sh

. common.sh
check_cookie
read_args

#debug

SBCONF=/etc/sickbeard/sickbeard.conf
SBPROG=/Alt-F/opt/SickBeard

SABHOME=/var/lib/sabnzbd
SABCONF=/etc/sabnzbd/sabnzbd.conf
SABPROG=/opt/SABnzbd/SABnzbd.py

SMBCF=/etc/samba/smb.conf

if test -n "$submit"; then

	if test -n "$conf_dir"; then
		conf_dir=$(httpd -d $conf_dir)
	fi

	if test "$(basename $conf_dir)" = "Public"; then
		msg "You must create a folder for Sickbeard." 
	elif ! res=$(check_folder "$conf_dir"); then
		msg "$res"
	fi

	if rcsickbeard status >& /dev/null; then
		sbworking=yes
		html_header
		busy_cursor_start
		rcsickbeard stop >& /dev/null
		while rcsickbeard status >& /dev/null; do
			usleep 200000
		done
	fi

	if test -f $SABPROG; then
		if ! test -f $SABHOME/scripts/autoProcessTV.cfg; then
			# copy SickBeard postprocess script to SABnzbd
			# autoProcessTV.cfg must be edited by the user if he adds a password to SAB/Sick
			mkdir -p $SABHOME/scripts; chown -R sabnzbd:TV $SABHOME
			cp $SBPROG/autoProcessTV/* $SABHOME/scripts/
			cp $SABHOME/scripts/autoProcessTV.cfg.sample $SABHOME/scripts/autoProcessTV.cfg
		fi

		sab_apikey=$(sed -n 's/^api_key[[:space:]]*=[[:space:]]*\(.*\)/\1/p' $SABCONF)
		if test -z "$sab_apikey"; then
			sab_apikey=$(uuidgen | tr -d '-')
			sed -i "s/^api_key.*/api_key = $sab_apikey/" $SABCONF
		fi
		sed -i "s/^sab_apikey.*/sab_apikey = $sab_apikey/" $SBCONF
	fi

	sed -i "s|^root_dirs.*=.*|root_dirs = 0\|$conf_dir|" $SBCONF
	#sed -i "s|^nzb_dir.*=.*|nzb_dir = $conf_dir|" $SBCONF # for BlackHole

	if test -n "$downld"; then
		sed -i "s/nzb_method.*=.*/nzb_method = $downld/" $SBCONF
	fi

	chown -R sickbeard:TV $conf_dir
	chmod g+rwxs $conf_dir

	if ! grep -q '\[SickBeard\]' $SMBCF; then
		cat <<EOF >> $SMBCF

[SickBeard]
	comment = SickBeard download area
	path = $conf_dir
	valid users = +TV
	available = yes
	read only = yes
EOF
	else
		sed -i "/\[SickBeard\]/,/\[.*\]/ { s|path.*|path = $conf_dir|}" $SMBCF
	fi

	if rcsmbstatus >& /dev/null; then
		rcsmb reload >& /dev/null
	fi

	if test -n "$sbworking"; then
		rcsickbeard start >& /dev/null
		busy_cursor_end
		js_gotopage /cgi-bin/user_services.cgi
	fi

elif test -n "$webPage"; then

	PORT=$(sed -n '/^web_port/s/.*= *\([0-9]*\)/\1/p' $SBCONF)
	PROTO="http"
	if grep -q '^enable_https.*=.*1' $SBCONF; then
		PROTO="https"
	fi

	embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT" "SickBeard Page"	
fi

#enddebug
#exit 0

gotopage /cgi-bin/user_services.cgi
