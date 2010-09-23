#!/bin/sh

. common.sh
check_cookie
read_args

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
		loadsave_settings -cf > /dev/null 2>&1
		;;

	LoadSettings)
		settings=$(httpd -d "$(echo $settings)")
		if test -n "$settings"; then
			loadsave_settings -lf "$settings"
		else
			msg "You must select a settings set."
		fi
		;;

	*)
		echo Hu? ;;

esac

#enddebug
gotopage /cgi-bin/settings.cgi


