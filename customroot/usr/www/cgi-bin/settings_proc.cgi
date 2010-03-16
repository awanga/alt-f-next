#!/bin/sh

. common.sh
check_cookie
read_args

#debug

case $action in

	SaveSettings)
		loadsave_settings -sf > /dev/null 2>&1
		if test $? = 1; then
			msg "No changes since last save"
		fi
		;;

	ClearSettings)
		loadsave_settings -cf > /dev/null 2>&1
		;;

	LoadSettings)
		settings=$(httpd -d $(echo $settings))
		loadsave_settings -lf "$settings"
		;;

	*)
		echo Hu? ;;

esac

#enddebug
gotopage /cgi-bin/settings.cgi


