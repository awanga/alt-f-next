#!/bin/sh

# This script is launched and respawn by init.
# It watchs for a running inetd every three minutes and if needed launchs one,
# with only minimum services active. 
# To recover from a damage or missing inetd.conf just copy inetd.conf.default over it

INETD_SCONF=/etc/inetd.conf.default
SERRORL=/var/log/systemerror.log

while true; do
	sleep 180
	if start-stop-daemon -S -q -x inetd -- $INETD_SCONF; then
		msg="watch-inetd: inetd not running, restarting it with an alternative minimum safe configuration."
		logger -t info $msg
		echo "<li>$msg</li>" >> $SERRORL
	fi
done
