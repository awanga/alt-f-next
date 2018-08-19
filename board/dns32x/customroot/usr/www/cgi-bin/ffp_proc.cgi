#!/bin/sh

. common.sh
read_args
check_cookie

#debug

busy_cursor_start
echo "<pre>"

if test -n "$Submit"; then
	for i in $(seq 1 $cnt); do
		srv=$(eval echo \$ffp_$i)
		srv=$(httpd -d "$srv")
		if test -n "$srv"; then
			enabled="$enabled $srv"
			if ! test -x $srv; then
				ch=yes
				chmod +x $srv
				PATH=/ffp/bin:/ffp/sbin:$PATH $srv start
			fi
		fi
	done

	for srv in $(ls /ffp/start/*.sh); do
		if ! echo $enabled | grep -q $srv; then
			if test -x $srv; then
				ch=yes
				PATH=/ffp/bin:/ffp/sbin:$PATH $srv stop
				chmod -x $srv
			fi
		fi
	done
fi

busy_cursor_end
echo "</pre>"
if test -n "$ch"; then
	goto_button Continue /cgi-bin/ffp.cgi
	echo "</body></html>"
else
	js_gotopage /cgi-bin/ffp.cgi
fi

