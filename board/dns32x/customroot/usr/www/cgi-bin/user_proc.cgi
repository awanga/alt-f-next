#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_MISC=/etc/misc.conf

uscript=$(httpd -d "$user_script")

if test -n "$uscript"; then

	sdir=$(dirname $uscript 2>/dev/null)
	if ! find_mp "$sdir" >& /dev/null; then
		msg "The full path name of an on disk file such as /mnt/sda2/mybootscript.sh or /mnt/md0/... must be supplied. The file will be overwritten if it exists or created if needed."
	fi

	mkdir -p "$sdir"
	httpd -d "$userscript" | dos2unix > $uscript
	chmod +x,og-wx "$uscript" 
fi

if test -z "$create_log"; then
	create_log="no"
fi

sed -i -e '/^USER_SCRIPT/d' -e '/^USER_LOGFILE/d' $CONF_MISC >& /dev/null
echo -e "USER_SCRIPT=\"$uscript\"\nUSER_LOGFILE=\"$create_log\"" >> $CONF_MISC

#enddebug
gotopage /cgi-bin/user_services.cgi

