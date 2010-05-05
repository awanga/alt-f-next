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
	grep -q -e "^$i" /etc/inetd.conf
	st=$?
	if test -z "$serv" -a "$st" = "0"; then
		inetd_change=1
		sed -i s/$i/#$i/ /etc/inetd.conf
	elif test "$serv" = "enable" -a "$st" != "0"; then
		inetd_change=1
		sed -i s/#$i/$i/ /etc/inetd.conf
	fi
done

if test "$inetd_change" = 1; then
	kill -HUP $(pidof inetd)
fi

fi

#enddebug
gotopage /cgi-bin/net_services.cgi

