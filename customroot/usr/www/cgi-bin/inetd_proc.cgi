#!/bin/sh

. common.sh
read_args
check_cookie

#debug

if test -n "$Configure"; then
	if test -f $PWD/${Configure}.cgi; then
		gotopage /cgi-bin/${Configure}.cgi
	else
		write_header "$Configure setup"
		echo "<p>Write me</p>"
		back_button
		echo "</body></html>"
		exit 0
	fi

elif test -n "$Submit"; then

	ssrvs="$(httpd -d $Submit)"

	for i in $ssrvs; do
		serv=$(eval echo \$$i)
		if test "$serv" = "enable"; then
			rcinetd enable $i >& /dev/null
		else
			rcinetd disable $i >& /dev/null
		fi
	done
fi

#enddebug
gotopage /cgi-bin/net_services.cgi

