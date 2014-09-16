#!/bin/sh

. common.sh
check_cookie
read_args

#debug

NZBCONF=/etc/nzbget.conf
SMBCF=/etc/samba/smb.conf

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
		
	sed -i 's|^MainDir=.*|MainDir='"$conf_dir"'|' $NZBCONF

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

	PROTO="http"
	PORT=$(awk -F= '/^ControlPort/{print $2}' $NZBCONF)
	
	if echo $HTTP_REFERER | grep -q 'https://'; then
		if grep -q '^SecureControl=yes' $NZBCONF; then
			PROTO="https"
			PORT=$(awk -F= '/^SecurePort/{print $2}' $NZBCONF)
		fi
	fi

	embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT" "NZBget Page"
fi

gotopage /cgi-bin/user_services.cgi
