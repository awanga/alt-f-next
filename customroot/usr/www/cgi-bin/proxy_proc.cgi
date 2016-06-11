#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/wgetrc

comment() {
	for i in http_proxy https_proxy ftp_proxy proxy_password proxy_user use_proxy; do
		sed -i "s/^$i/#!#$i/" $CONFF >& /dev/null
	done
}

uncomment() {
	for i in http_proxy https_proxy ftp_proxy proxy_password proxy_user use_proxy; do
		sed -i "s/^#!#$i/$i/" $CONFF >& /dev/null
	done
}

remove() {
	for i in http_proxy https_proxy ftp_proxy proxy_password proxy_user use_proxy; do
		sed -i "/^#!#$i/d" $CONFF >& /dev/null
	done
}

if test "$useproxy" = "yes"; then
	comment
	if test -n "$http_port"; then prt=":$(httpd -d $http_port)"; fi
	if test -z "$http_proxy"; then
		uncomment
		msg "If you have to use a proxy,\n you must specify the http proxy server."
	else
		echo http_proxy=$(httpd -d ${http_proxy}$prt) >> $CONFF
	fi

	if test -n "$https_port"; then prt=":$(httpd -d $https_port)"; fi
	if test -z "$https_proxy"; then
		uncomment
		msg "If you have to use a proxy,\n you must specify the http proxy server."
	else
		echo https_proxy=$(httpd -d ${https_proxy}$prt) >> $CONFF
	fi

	if test -n "$ftp_port"; then prt=":$(httpd -d $ftp_port)"; fi	
	if test -n "$ftp_proxy"; then
		echo ftp_proxy=$(httpd -d ${ftp_proxy}$prt) >> $CONFF
	fi

	if test -z "$anonproxy"; then
		if test -n "$proxy_user"; then
			echo proxy_user=$(httpd -d $proxy_user) >> $CONFF
		else
			uncomment
			msg "The Username can't be empty."
		fi

		proxy_password=$(checkpass "$proxy_password")
		if test $? != 0; then
			uncomment
			msg "$proxy_password"
		else
			echo proxy_password=$proxy_password >> $CONFF
		fi
	fi
	echo use_proxy=on >> $CONFF
	remove
	chmod og-rwx $CONFF
elif test -f $CONFF; then
	sed -i '/^use_proxy/d' $CONFF
	echo "use_proxy=off" >> $CONFF
	chmod og-rwx $CONFF
fi

#enddebug
gotopage /cgi-bin/proxy.cgi

