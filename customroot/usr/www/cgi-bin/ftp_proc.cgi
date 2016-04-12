#!/bin/sh

. common.sh
check_cookie

CONFF=/etc/vsftpd.conf
CONFU=/etc/vsftpd.user_list
CONFS=/etc/init.d/S63vsftpd

vars="chroot_local_user allow_writeable_chroot anonymous_enable anon_upload_enable ssl_enable force_local_logins_ssl force_local_data_ssl userlist_enable implicit_ssl syslog_enable xferlog_enable"

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

sed -i '/implicit_ssl/d' $CONFF 
echo "#implicit_ssl=$implicit_ssl #!# Alt-F usage, don't uncomment" >> $CONFF

if test "$ftp_inetd" = "inetd"; then
	rcvsftpd stop >& /dev/null
	rcinetd enable ftp ftps >& /dev/null
	if test "$implicit_ssl" = "no"; then
		rcinetd disable ftps >& /dev/null
	fi
	#sed -i 's/^TYPE=/#TYPE=/' $CONFS
	
else
	rcinetd disable ftp ftps >& /dev/null
	#sed -i 's/^#TYPE=/TYPE=/' $CONFS
	rcvsftpd restart >& /dev/null
fi

#enddebug
gotoback $from_url ftp.cgi
