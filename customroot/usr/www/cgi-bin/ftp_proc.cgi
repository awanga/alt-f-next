#!/bin/sh

. common.sh
check_cookie

CONFF=/etc/vsftpd.conf

vars="anonymous_enable anon_upload_enable ssl_enable force_local_logins_ssl force_local_data_ssl"

for i in $vars; do eval $i=NO; done

read_args

#debug

if test -n "$anon_root"; then
	anon_root="$(httpd -d $anon_root)"
	sed -i '/^anon_root=/d' $CONFF
	echo "anon_root=$anon_root" >> $CONFF
fi

for i in $vars; do
	sed -i '/^'$i'/d' $CONFF
	echo "$i=$(eval echo \$$i)" >> $CONFF
done

#enddebug
gotopage /cgi-bin/ftp.cgi
