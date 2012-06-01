#!/bin/sh

. common.sh
check_cookie
read_args

SABHOME=/var/lib/sabnzbd
SABCONF=/etc/sabnzbd/sabnzbd.conf

SBPROG=/opt/Sick-Beard
SBCONF=/etc/sickbeard.conf

CPCONF=/etc/couchpotato.conf

SMBCF=/etc/samba/smb.conf

#debug

# this is to disappear after RC3 (included in common.sh)
# -----------------------------------------------------
check_folder() {
	if ! test -d "$1"; then
		echo "\"$1\" does not exists or is not a folder."
		return 1
	fi

	tmp=$(readlink -f "$1")
	while ! mountpoint -q "$tmp"; do
		tmp=$(dirname "$tmp")
	done

	if test "$tmp" = "/" -o "$tmp" = "."; then
		echo "\"$1\" is not on a filesystem."
		return 1
	fi

	if test "$tmp" = "$1"; then
		echo "\"$1\" is a filesystem root, not a folder."
		return 1
	fi
}
# ----------------------------------------

daemon_stop() {
    $1 stop
    for i in $(seq 1 30); do
        if ! $1 status >& /dev/null; then break; fi
        sleep 1
    done
}

if test -n "$submit"; then

	if test -n "$conf_dir"; then
		conf_dir=$(httpd -d $conf_dir)
	fi

	if test "$(basename $conf_dir)" = "Public"; then
		msg "You must create a folder for SABnzbd." 
	elif ! res=$(check_folder "$conf_dir"); then
		msg "$res"
	fi

	sed -i -e 's|^dirscan_dir.*|dirscan_dir = '"$conf_dir"'|' \
		-e 's|^download_dir.*|download_dir = '"$conf_dir"'/Incomplete|' \
		-e 's|^complete_dir.*|complete_dir = '"$conf_dir"'/Complete|' $SABCONF

	if test -e $SBCONF -a ! -d $SABHOME/scripts; then # SickBeard is installed
		#daemon_stop rcsickbeard
	
		# copy SickBeard postprocess script to SAPnzbd
		# autoProcessTV.cfg must be edited by the user if he adds a password to SAB/Sick
		mkdir -p $SABHOME/scripts
		cp $SBPROG/autoProcessTV/* $SABHOME/scripts/
		cp $SABHOME/scripts/autoProcessTV.cfg.sample $SABHOME/scripts/autoProcessTV.cfg
	
		# offer choice btweeen sabnzbd and nzbget news grabber? here or in sb/cp web pages? 
		#sed -i "s/^sab_apikey.*/sab_apikey = $sab_apikey/" $SBCONF
		#sed -i "s|^sab_host.*|sab_host = http://$(hostname -i | tr -d ' '):8082/|" $SBCONF
		#sed -i "s/^nzb_method.*/nzb_method = sabnzbd/" $SBCONF
	fi

#	if test -e $CPCONF; then # CouchPotato is installed
#		daemon_stop rccouchpotato
#
#		# offer choice btweeen sabnzbd and nzbget news grabber? here or in sb/cp web pages? 
#		sed -i "/\[Sabnzbd\]/,/\[.*\]/s/^apikey.*/apikey = $sab_apikey/" $CPCONF
#	fi

	if ! grep -q '\[SABnzbd\]' $SMBCF; then
		cat <<EOF >> $SMBCF

[SABnzbd]
	comment = SABnzbd download area
	path = $BASE/SABnzbd
	valid users = +TV
	available = yes
	read only = yes
EOF
	else
		sed -i "/\[SABnzbd\]/,/\[.*\]/ { s|path.*|path = $conf_dir|}" $SMBCF
	fi

	rcsmb reload >& /dev/null

	chown -R sabnzbd:TV /etc/sabnzbd "$conf_dir" $SABHOME
	chmod -R g+rwxs "$conf_dir"

	gotopage /cgi-bin/user_services.cgi

elif test -n "$webPage"; then

	PORT=$(awk '/[misc]/{ while (st = getline) { if ($1 == "port") {print $3; exit}}}' $SABCONF)
	PROTO="http"

	if ! rcsabnzbd status >& /dev/null; then
		rcsabnzbd start >& /dev/null
	fi

	embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT"

fi
