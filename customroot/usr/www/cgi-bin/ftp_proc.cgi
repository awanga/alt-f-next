#!/bin/sh

. common.sh
check_cookie

CONFF=/etc/vsftpd.conf
CONFU=/etc/vsftpd.user_list

vars="chroot_local_user anonymous_enable anon_upload_enable ssl_enable \
force_local_logins_ssl force_local_data_ssl userlist_enable"

for i in $vars; do eval $i=no; done

read_args

#debug

if test -n "$anon_root"; then
	anon_root=$(httpd -d "$anon_root")
	sed -i '/^anon_root=/d' $CONFF
	echo anon_root="$anon_root" >> $CONFF
fi

if test -n "$denyusers"; then
	denyusers=$(httpd -d $denyusers)
	userlist_enable=yes
else
	denyusers=""
fi
echo $denyusers | tr ' ' '\n' > $CONFU

for i in $vars; do
	sed -i '/^'$i'/d' $CONFF
	echo "$i=$(eval echo \$$i)" >> $CONFF
done

#enddebug
gotopage /cgi-bin/inetd.cgi
