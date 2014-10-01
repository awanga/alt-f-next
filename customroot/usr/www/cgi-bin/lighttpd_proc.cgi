#!/bin/sh

. common.sh
check_cookie

CONF_LIGHTY=/etc/lighttpd/lighttpd.conf
CONF_LIGHTY2=/etc/lighttpd/modules.conf
CONF_PHP=/etc/php.ini
PHP_EDIR=/usr/lib/php5/extensions
CONF_SSL=/etc/lighttpd/conf.d/ssl.conf
CONF_AUTH=/etc/lighttpd/conf.d/auth.conf
SMBCF=/etc/samba/smb.conf

vars="ipv6 ssl auth wdav userdir dirlist accesslog php"
for i in $vars; do eval $i=no; done

if test -x /usr/bin/php; then
	for i in $(ls $PHP_EDIR); do
		bi=$(basename $i .so)
		eval $bi=no
	done
fi

read_args

#debug

if test -n "$WebPage"; then
	PORT=$(grep ^server.port $CONF_LIGHTY | cut -d" " -f3)
	PROTO="http"
	if echo $HTTP_REFERER | grep -q 'https://'; then
		if grep -q '^include "conf.d/ssl.conf"' $CONF_LIGHTY; then
			PORT=$(sed -n 's/$SERVER\["socket"\] == ":\(.*\)".*/\1/p' $CONF_SSL)
			PROTO="https"
		fi
	fi
	
	embed_page "$PROTO://${HTTP_HOST%%:*}:${PORT}" "Lighttpd Page"
fi

if test -z "$sslport"; then sslport="8443"; fi
if test -z "$port"; then port="8080"; fi

if test -n "$sroot"; then sroot=$(httpd -d "$sroot"); fi

if test "$(basename $sroot)" = "Public"; then
	msg "You must create a 'Server Root' folder."
fi

if ! res=$(check_folder $sroot); then
	msg "$res"
else
	chown lighttpd:network "$sroot"
	chmod og-w "$sroot"
fi

if ! test -d "$sroot/htdocs"; then
	mkdir -p "$sroot/htdocs"
	chown lighttpd:network "$sroot/htdocs"
	chmod og-w "$sroot/htdocs"
	echo "<html><body><p>Hello Dolly</body></html>" > "$sroot/htdocs/hello.html"
	echo "<?php phpinfo(); ?>" > "$sroot/htdocs/hello.php"
	chmod go-w "$sroot/htdocs/hello.html" "$sroot/htdocs/hello.php"
fi

if ! grep -q '\[WebData\]' $SMBCF; then
	cat <<EOF >> $SMBCF

[WebData]
	comment = Lighttpd area
	path = $sroot/htdocs
	public = no 
	available = yes
	read only = yes
EOF

else
	sed -i "/\[WebData\]/,/\[.*\]/ { s|path.*|path = $sroot/htdocs|}" $SMBCF
fi

sed -i 's|^var.server_root.*$|var.server_root = "'$(httpd -d $sroot)'"|' $CONF_LIGHTY
sed -i 's|^server.port.*$|server.port = '$(httpd -d $port)'|' $CONF_LIGHTY

#IPv6
opt="enable"
if test "$ipv6" = "no"; then opt="disable"; fi
sed -i 's|^server.use-ipv6.*$|server.use-ipv6 = "'$opt'"|' $CONF_LIGHTY

#SSL
cmt="#"
if test "$ssl" = "yes"; then cmt=""; fi
sed -i 's|.*\(include.*ssl.conf.*\)|'$cmt'\1|' $CONF_LIGHTY

#SSL port
sed -i 's|^$SERVER\["socket"\].*$|$SERVER\["socket"\] == ":'$(httpd -d $sslport)'" \{|' $CONF_SSL

#auth
cmt="#"
if test "$wdav" = "yes" -a "$user" != "anybody"; then cmt=""; fi
sed -i 's|.*\(include.*auth.conf.*\)|'$cmt'\1|' $CONF_LIGHTY2

#webdav
cmt="#"
if test "$wdav" = "yes"; then
	wdavd="$sroot/htdocs/webdav"
	if ! test -d "$wdavd"; then
		mkdir -p "$wdavd"
		chown lighttpd:network "$wdavd"
		chmod og-w "$wdavd"
	fi
	cmt=""
fi
sed -i 's|.*\(include.*webdav.conf.*\)|'$cmt'\1|' $CONF_LIGHTY2

#webdav user
cmt=""
opt="valid-user"
if test "$user" = "anybody"; then
	cmt="#"
elif test "$user" != "anyuser"; then
	opt="user=$user";
fi
sed -i 's|.*\(auth.require.*webdav.*"require" *=> *"\)\(.*\)"\(.*\)|'$cmt'\1'$opt'"\3|' $CONF_AUTH


cmt="#"
if test "$userdir" = "yes"; then cmt=""; fi
sed -i 's|.*\(include.*userdir.conf.*\)|'$cmt'\1|' $CONF_LIGHTY2

cmt="#"
if test "$dirlist" = "yes"; then cmt=""; fi
sed -i 's|.*\(include.*dirlisting.conf.*\)|'$cmt'\1|' $CONF_LIGHTY

cmt="#"
if test "$accesslog" = "yes"; then cmt=""; fi
sed -i 's|.*\(include.*access_log.conf.*\)|'$cmt'\1|' $CONF_LIGHTY

cmt="#"
if test "$php" = "yes"; then cmt=""; fi
sed -i 's|.*\(include.*fastcgi.conf.*\)|'$cmt'\1|' $CONF_LIGHTY2

if test "$php" = "yes"; then
	if test -z "$php_maxupload"; then php_maxupload="10M"; fi

	sed -i 's|.*upload_max_filesize.*|upload_max_filesize = '$(httpd -d $php_maxupload)'|' $CONF_PHP
	sed -i 's|.*post_max_size.*|post_max_size = '$(httpd -d $php_maxupload)'|' $CONF_PHP
	for i in $(ls $PHP_EDIR); do
		bi=$(basename $i .so)
		cmt=";"
		if test "$(eval echo \$$bi)" = "yes"; then cmt=""; fi
		sed -i 's|.*\(extension='$i'\)|'$cmt'\1|' $CONF_PHP
	done
fi

if rclighttpd status >& /dev/null; then
	rclighttpd restart >& /dev/null
fi

#enddebug
gotopage /cgi-bin/net_services.cgi
