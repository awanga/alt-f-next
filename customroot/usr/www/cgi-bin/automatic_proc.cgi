#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_AUTO=/etc/automatic.conf

if test -n "$Submit"; then

	sed -i '/\(^feed\|^filter\| *cookie\| *folder\|^interval\|^start-torrents\)/d' $CONF_AUTO

	for i in $(seq 0 $feed_cnt); do
		feed=$(eval echo \$feed_$i)
		cookie=$(eval echo \$cookie_$i)

		if test -z "$feed"; then continue; fi
		if test -n "$cookie"; then
			cookie=$(httpd -d $cookie)
		fi

		echo -e "feed = { url => \"$(httpd -d $feed)\"\n\tcookies => \"$cookie\" }" >> $CONF_AUTO
	done

	for i in $(seq 0 $pattern_cnt); do
		pattern=$(eval echo \$pattern_$i)
		folder=$(eval echo \$folder_$i)

		if test -z "$pattern"; then continue; fi
		if test -n "$folder"; then
			folder=$(httpd -d $folder)
		fi

		echo -e "filter = { pattern => \"$(httpd -d $pattern)\"\n\tfolder => \"$folder\" }" >> $CONF_AUTO
	done

	echo "interval = $interval" >> $CONF_AUTO

	if test -z "$start_downloads"; then
		start_downloads="no"
	fi
	echo "start-torrents = $start_downloads" >> $CONF_AUTO

fi

#enddebug
gotopage /cgi-bin/user_services.cgi
