#!/bin/sh

. common.sh
check_cookie
read_args

SABHOME=/var/lib/sabnzbd
SABCONF=/etc/sabnzbd/sabnzbd.conf

SBPROG=/opt/SickBeard
SBCONF=/etc/sickbeard.conf

CPCONF=/etc/couchpotato.conf

SMBCF=/etc/samba/smb.conf

#debug

daemon_stop() {
    $1 stop
    for i in $(seq 1 30); do
        if ! $1 status >& /dev/null; then break; fi
        sleep 1
    done
}

if test -n "$update"; then
	if test -z $version; then
		msg "You have to supply the SABnzbd version to update to."
	else
		VER=$(httpd -d $version)
		if test "$VER" = "$(httpd -d $curver)"; then
			msg "You are already using version $VER"
		fi

		TBALL=SABnzbd-$VER-src.tar.gz
		SITE=http://master.dl.sourceforge.net/project/sabnzbdplus/sabnzbdplus/$VER

		html_header "SABnzbd update"
		echo "<p>Downloading SABnzbd...<pre>"
		if ! wget --progress=dot:mega -O /tmp/$TBALL $SITE/$TBALL; then
			rm -f /tmp/$TBALL
			echo "</pre><p>Downloading failed.<br>$(back_button)"
			exit 1
		fi

		echo "</pre><p>Stopping SABnzbd..."
		rcsabnzbd stop >& /dev/null
		while rcsabnzbd status >& /dev/null; do usleep 200000; done

		aufs.sh -n
		SABPROG=/Alt-F/opt/SABnzbd
		mkdir -p $SABPROG
		echo "<p>Extracting SABnzbd..."
		if ! tar -C /Alt-F/opt -xzf /tmp/$TBALL >& /dev/null; then
			rm -f /tmp/$TBALL
			echo "<p>Extraction of SABnzbd failed.<br>$(back_button)"
			aufs.sh -r
			exit 1
		fi
		rm -f /tmp/$TBALL

		cp -a $SABPROG-$VER/* $SABPROG
		rm -rf $SABPROG-$VER
		chown -R sabnzbd:TV $SABPROG
		aufs.sh -r

		echo "<p>Starting SABnzbd..."
		rcsabnzbd start >& /dev/null
		for i in $(seq 1 300); do
			if rcsabnzbd status >& /dev/null; then
				break
			else
				usleep 200000
			fi
		done
	fi

	js_gotopage /cgi-bin/user_services.cgi

elif test -n "$submit"; then

	if test -n "$conf_dir"; then
		conf_dir=$(httpd -d $conf_dir)
	fi

	if test "$(basename $conf_dir)" = "Public"; then
		msg "You must create a folder for SABnzbd." 
	elif ! res=$(check_folder "$conf_dir"); then
		msg "$res"
	fi

	if rcsabnzbd status >& /dev/null; then
		sabworking=yes
		html_header
		busy_cursor_start
		rcsabnzbd stop >& /dev/null
		while rcsabnzbd status >& /dev/null; do
			usleep 200000
		done
	fi

	sed -i -e 's|^dirscan_dir.*|dirscan_dir = '"$conf_dir"'|' \
		-e 's|^download_dir.*|download_dir = '"$conf_dir"'/Incomplete|' \
		-e 's|^complete_dir.*|complete_dir = '"$conf_dir"'/Complete|' $SABCONF

	sab_apikey=$(sed -n 's/^api_key[[:space:]]*=[[:space:]]*\(.*\)/\1/p' $SABCONF)
	if test -z "$sab_apikey"; then
		sab_apikey=$(uuidgen | tr -d '-')
		sed -i "s/^api_key.*/api_key = $sab_apikey/" $SABCONF
	fi

	if test -e $SBCONF -a ! -d $SABHOME/scripts; then # SickBeard is installed
		#daemon_stop rcsickbeard
	
		# copy SickBeard postprocess script to SAPnzbd
		# autoProcessTV.cfg must be edited by the user if he adds a password to SAB/Sick
		mkdir -p $SABHOME/scripts
		cp $SBPROG/autoProcessTV/* $SABHOME/scripts/
		cp $SABHOME/scripts/autoProcessTV.cfg.sample $SABHOME/scripts/autoProcessTV.cfg
	fi

	# existing installations migh miss CouchPotato movie category support
	if ! grep -q '\[\[movie\]\]' $SABCONF; then
		sed -i '/^\[categories\]/a \
			\[\[movie\]\] \
			priority = -100 \
			pp = "" \
			name = movie \
			script = Default \
			newzbin = Movies \
			dir = Movies' $SABCONF
	fi

	if ! grep -q '\[SABnzbd\]' $SMBCF; then
		cat <<EOF >> $SMBCF

[SABnzbd]
	comment = SABnzbd download area
	path = $conf_dir
	valid users = +TV
	available = yes
	read only = yes
EOF
	else
		sed -i "/\[SABnzbd\]/,/\[.*\]/ { s|path.*|path = $conf_dir|}" $SMBCF
	fi

	if rcsmbstatus >& /dev/null; then
		rcsmb reload >& /dev/null
	fi

	chown -R sabnzbd:TV $SABHOME /etc/sabnzbd "$conf_dir"
	chmod -R g+rwxs "$conf_dir"

	if test -n "$sabworking"; then
		rcsabnzbd start >& /dev/null
		busy_cursor_end
		js_gotopage /cgi-bin/user_services.cgi
	fi

	gotopage /cgi-bin/user_services.cgi

elif test -n "$webPage"; then

	PORT=$(awk '/[misc]/{ while (st = getline) { if ($1 == "port") {print $3; exit}}}' $SABCONF)
	PROTO="http"

	if grep -q '^enable_https.*=.*1' $SABCONF; then
		PROTO="https"
		PORT=$(awk '/[misc]/{ while (st = getline) { if ($1 == "https_port") {print $3; exit}}}' $SABCONF)
	fi

	embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT" "SABnzbd Page"

fi
