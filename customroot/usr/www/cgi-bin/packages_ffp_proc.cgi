#!/bin/sh

download() {
    wget -q http://www.inreto.de/dns323/fun-plug/0.5/packages/$1 \
        -O /tmp/$1
    if test $? = 1; then
        wget -q http://www.inreto.de/dns323/fun-plug/0.5/extra-packages/All/$1 \
        -O /tmp/$1
        return $?
    fi
    return 0
}

. common.sh
check_cookie
read_args

#debug

s="<strong>"
es="</strong>"

if test "$install" = "Install"; then
	if test "$part" = "none"; then
		msg "You must select a partition"
	fi

	TMPF=/tmp/fun_plug.tgz
	SITE=http://www.inreto.de/dns323/fun-plug/0.5/fun_plug.tgz
	#SITE=http://silver/~jcard/fun_plug.tgz

	write_header "Installing FFP"

	echo "<p>$s Downloading... $es </p><pre>"
	wget --progress=dot:mega  $SITE -O $TMPF #\ 
		# 2>&1 | sed -nu -e 's/^ *=>.*//' -e 's/^ //p'
	st=$?
	echo "</pre>"

	if test $st = 0; then
		echo "<p> $s Installing... "
		part=$(httpd -d $part)
		mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)
		mkdir -p $mp/ffp
		tar -C $mp/ffp -xzf $TMPF

		if test $? = 0; then
			ln -sf $mp/ffp /ffp
			chown root.root /ffp/bin/busybox
			chmod 0755 /ffp/bin/busybox
			chmod u+s /ffp/bin/busybox
			chmod -x /ffp/start/*
			echo " success. $es </p>"
		else
			echo " fail. $es </p>"
		fi
	else
		echo "<p> $s Downloading failed. $es </p>"
	fi
	rm -f $TMPF
	echo  "<form action=\"/cgi-bin/packages_ffp.cgi\">
	<input type=submit value=\"Continue\"></form></body></html>"
	exit

elif test -n "$Remove"; then
    /ffp/sbin/funpkg -r $Remove >/dev/null 2>&1

elif test -n "$Install"; then
    download $Install.tgz
    if test $? = 0; then
        /ffp/sbin/funpkg -i /tmp/$Install.tgz >/dev/null 2>&1
        rm /tmp/$Install.tgz
    fi

elif test -n "$Update"; then
    download $Update.tgz
    if test $? = 0; then
# FIXME -- get and use currently installed package    
#        for i in $(grep -e '/ffp/start/.*.sh' -e '/ffp/etc/.*.conf' /ffp/var/packages/$Update); do
#            cp $i $i-safe
#        done
        /ffp/sbin/funpkg -u /tmp/$Update.tgz >/dev/null 2>&1
        rm /tmp/$Update.tgz
    fi
fi

gotopage /cgi-bin/packages_ffp.cgi
