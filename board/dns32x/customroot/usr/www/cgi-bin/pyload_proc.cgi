#!/bin/sh

. common.sh
check_cookie
read_args

#debug

PYLCONF=/etc/pyload/pyload.conf
SMBCF=/etc/samba/smb.conf

if test -n "$submit"; then

	if test -n "$conf_dir"; then
		conf_dir=$(httpd -d $conf_dir)
	fi

	if test "$(basename $conf_dir)" = "Public"; then
		msg "You must create a folder for pyLoad." 
	elif ! res=$(check_folder "$conf_dir"); then
		msg "$res"
	fi

	if rcpyload status >& /dev/null; then
		pyloadworking=yes
		rcpyload stop >& /dev/null
		while rcpyload status >& /dev/null; do
			usleep 200000
		done
	fi

	sed -i '/download_folder/s|\(.*=\).*|\1 '$conf_dir'|' $PYLCONF	

	if ! grep -q '\[pyLoad\]' $SMBCF; then
		cat <<EOF >> $SMBCF

[pyLoad]
	comment = pyLoad download area
	path = $conf_dir
	valid users = +BT
	available = yes
	read only = yes
EOF
	else
		sed -i "/\[pyLoad\]/,/\[.*\]/ { s|path.*|path = $conf_dir|}" $SMBCF
	fi
	
	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi

	if test -n "$pyloadworking"; then
		rcpyload start >& /dev/null
	fi

elif test -n "$webPage"; then

	PROTO="http"
	PORT=$(sed -n '/^webinterface/,/^$/s/.*port.*=[[:space:]]*\(.*\)/\1/p' $PYLCONF)
	if echo $HTTP_REFERER | grep -q 'https://'; then
			PROTO="https"
	fi

	embed_page "$PROTO://${HTTP_HOST%%:*}:$PORT" "pyLoad Page"
fi

gotopage /cgi-bin/user_services.cgi
