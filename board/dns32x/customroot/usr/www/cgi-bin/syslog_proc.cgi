#!/bin/sh

# Copyright (c) 2010 Augusto Bott <augusto at bott com br>
# Licence GNU GPL, see the /COPYING file for details

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/syslog.conf

cmd="log_internal log_remote log_remote_host log_remote_port log_drop_dups log_smaller_output"

if test -f $CONFF; then
	rm $CONFF
fi

for i in $cmd; do
	arg="$(eval echo \$$i)"
#	if test -z "$arg"; then continue; fi
	if test -z "$arg"; then 
		val=""
	else
		val=$(httpd -d "$arg")
	fi
	echo "$i=\"$val\"" >> $CONFF
done

if rcsyslog status >& /dev/null; then
	rcsyslog restart >& /dev/null
fi

#enddebug
gotopage /cgi-bin/syslog.cgi

