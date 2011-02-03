#!/bin/sh

. common.sh
check_cookie

if test "${CONTENT_TYPE%;*}" = "multipart/form-data"; then
	upfile=$(upload_file)
	action="Upload"
else
	read_args
fi

#debug

case $action in

	SaveSettings)
		res=$(loadsave_settings -sf)
		if test $? = 1; then
			msg "$res"
		fi
		if test -f /tmp/firstboot; then
			rm -f /tmp/firstboot
			gotopage /cgi-bin/status.cgi
		fi
		;;

	ClearSettings)
		loadsave_settings -cf >& /dev/null
		;;

	LoadSettings)
		settings=$(httpd -d "$(echo $settings)")
		if test -n "$settings"; then
			loadsave_settings -lf "$settings"
		else
			msg "You must select a settings set."
		fi
		;;

	Upload)
		res=$(loadsave_settings -lf $upfile 2>&1 )
		st=$?
		rm -f $upfile
		if test $st != 0; then
			msg "$res"
		fi
		;;

	Download)
		downfile=$(loadsave_settings -cs)
		download_file /tmp/$downfile
		rm -f /tmp/$downfile
		exit 0
		;;
esac

#enddebug
gotopage /cgi-bin/settings.cgi


