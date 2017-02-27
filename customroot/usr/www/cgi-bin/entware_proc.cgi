#!/bin/sh

. common.sh
read_args
check_cookie

#debug
#set -x

busy_cursor_start

if test -n "$Submit"; then
	for i in $(seq 1 $cnt); do
		srv=$(eval echo \$entware_$i)
		srv=$(httpd -d "$srv")
		if test -n "$srv"; then
			enabled="$enabled $srv"
			if ! test -x $srv; then
				chmod +x $srv
				PATH=/opt/bin:/opt/sbin:$PATH $srv start >& /dev/null
			fi
		fi
	done

	for srv in $(ls /opt/etc/init.d/S*); do
		if ! echo $enabled | grep -q $srv; then
			if test -x $srv; then
				PATH=/opt/bin:/opt/sbin:$PATH $srv stop >& /dev/null
				chmod -x $srv
			fi
		fi
	done

elif test -n "$StartNow"; then
	srv=$(httpd -d $StartNow)
	PATH=/opt/bin:/opt/sbin:$PATH sh $srv start >& /dev/null

elif test -n "$StopNow"; then
	srv=$(httpd -d $StopNow)
	PATH=/opt/bin:/opt/sbin:$PATH sh $srv stop >& /dev/null

fi

busy_cursor_end
js_gotopage /cgi-bin/entware.cgi
