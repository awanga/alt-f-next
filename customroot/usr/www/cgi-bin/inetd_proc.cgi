#!/bin/sh

. common.sh
read_args
check_cookie

CONFF=/etc/inetd.conf

#debug
#set -x 

if test -n "$Configure"; then
	gotopage /cgi-bin/${Configure}.cgi

elif test -n "$Submit"; then

	ssrv=$(awk '{if (substr($1,1,1) == "#") $1=substr($1,2); print $1}' $CONFF)

	for i in $ssrv; do
		serv=$(eval echo \$$i)
		if test "$serv" = "enable"; then
			to_enable="$to_enable $i"
		else
			to_disable="$to_disable $i"
		fi
	done

	# by default, use stunnel in inetd mode
	if echo "$to_enable" | grep -qE '(https|swats)'; then
		rcstunnel stop >& /dev/null
		rcstunnel disable >& /dev/null
	fi

	if test -n "$to_enable"; then rcinetd enable $to_enable >& /dev/null; fi
	if test -n "$to_disable"; then rcinetd disable $to_disable >& /dev/null; fi

	#enddebug
	gotopage /cgi-bin/net_services.cgi
fi
