#!/bin/sh

TMPF=/tmp/fun_plug.tgz
SITE=http://www.inreto.de/dns323/fun-plug/0.5/fun_plug.tgz
#SITE=http://silver/~jcard/fun_plug.tgz

. common.sh
check_cookie
read_args

if test "$part" = "none"; then
	msg "You must select a partition"
fi

write_header "Installing FFP"

s="<strong>"
es="</strong>"

#echo "<pre>$(set)</pre>"

dest="/cgi-bin/packages.cgi"

if test "$install" = "Install"; then
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
			dest="/cgi-bin/packages_proc.cgi"
		else
			echo " fail. $es </p>"
		fi
	else
		echo "<p> $s Downloading failed. $es </p>"
	fi
fi

rm -f $TMPF

echo  "<form action=\"$dest\">
	<input type=submit value=\"Continue\"></form></body></html>"
