#!/bin/sh

. common.sh
check_cookie

CONFF=/etc/vsftpd.conf
CONFU=/etc/vsftpd.user_list
CONFS=/etc/init.d/S63vsftpd

vars="chroot_local_user allow_writeable_chroot anonymous_enable anon_upload_enable \
ssl_enable force_local_logins_ssl force_local_data_ssl userlist_enable listen"

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
	sed -i "/^$i=/d" $CONFF
	echo "$i=$(eval echo \$$i)" >> $CONFF
done

if test "$listen" = "yes"; then
	rcinetd disable ftp ftps >& /dev/null
	rcvsftpd enable >& /dev/null
	rcvsftpd restart >& /dev/null
	sed -i 's/^#TYPE=/TYPE=/' $CONFS
else
	rcvsftpd disable >& /dev/null
	rcvsftpd stop >& /dev/null
	sed -i 's/^TYPE=/#TYPE=/' $CONFS
	rcinetd enable ftp ftps >& /dev/null
fi

#enddebug
gotopage /cgi-bin/inetd.cgi
