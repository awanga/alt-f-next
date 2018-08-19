#!/bin/sh

. common.sh
check_cookie

restart() {
	html_header
	busy_cursor_start

	hostname -f /etc/hostname >& /dev/null
	
	start-stop-daemon -K -x udhcpc >& /dev/null

	ifdown eth0 >& /dev/null
	sleep 1
	ifup eth0 >& /dev/null

	# FIXME: add 'reload' as 'restart' to all initscript services
	# that do not support reload and use 'rcall reload' instead
	# rcall restart >& /dev/null

	busy_cursor_end

	js_gotopage /cgi-bin/settings.cgi
}

if test "${CONTENT_TYPE%;*}" = "multipart/form-data"; then
	if ! upfile=$(upload_file); then
		msg "Error: Uploading failed: $upfile"
		exit 0
	fi
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
		;;

	ClearSettings) loadsave_settings -cf >& /dev/null ;;

	FormatFlashSettings) loadsave_settings -fm >& /dev/null ;;

	LoadSettings)
		settings=$(httpd -d "$(echo $settings)")
		if test -n "$settings"; then
			loadsave_settings -lf "$settings"
			restart
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
		restart
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


