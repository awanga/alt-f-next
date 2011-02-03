#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_MISC=/etc/misc.conf

uscript=$(httpd -d "$user_script")

if test -n "$uscript"; then
	if ! test -f "$uscript"; then
		msg "File does not exists."
	fi

	if ! test -x "$uscript"; then
		msg "File is not executable."
	fi

	# stat -t does give permissions in hex...
	chmod og-w "$uscript" 
fi

if test -z "$create_log"; then
	create_log="no"
fi

sed -i '/^USER_SCRIPT/d' $CONF_MISC >& /dev/null
sed -i '/^USER_LOGFILE/d' $CONF_MISC >& /dev/null

echo USER_SCRIPT=\"$uscript\" >> $CONF_MISC
echo USER_LOGFILE=\"$create_log\" >> $CONF_MISC

#enddebug
gotopage /cgi-bin/user_services.cgi

