#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/ipkg.conf

#debug

if test "$install" = "Install"; then

	if test "$part" = "none"; then
		msg "You must select a partition"
	fi

	# check that /Alt-F is a link, that points to a directory, and
	# that directory is a aufs union branch
	# If not, then create directory, aufs mount it, and create /Alt-F link
	if ! test -h /Alt-F -a \
		-d "$(readlink -f /Alt-F)" -a \
		"$(cat /sys/fs/aufs/*/br* | grep -o Alt-F)" = "Alt-F" ; then
			part=$(httpd -d $part)
			mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)
			mkdir -p $mp/Alt-F
			ln -sf $mp/Alt-F /Alt-F
			mount -t aufs -o remount,prepend:$mp/Alt-F=rw aufs /
	fi

	IPKG=ipkg_0.99.163_arm.ipk
	FEED=$(awk '/^src/{print $3}' $CONFF)
	DESTD=$(awk '/^dest/{print $3}' $CONFF)

	if test "$DESTD" != "/Alt-F"; then
		msg "Package destination directory must be /Alt-F"
	fi

	if ! test -d "$DESTD"; then
		msg "Package destination directory not found."
	fi
			
	TMPD=$(mktemp -d -t)
	wget -nv -P $TMPD $FEED/$IPKG >& /dev/null
	if test $? != 0; then
		rm -rf $TMPD
		msg "Downloading of $IPKG from $FEED failed."
	fi
	
	cd $TMPD
	ar x $IPKG # busybox ar is not extracting control: "ar: invalid ar header "
	tar xzf control.tar.gz
	awk '/^Package:/ {
			if( $2 != "ipkg") exit 1 }
		/^Architecture:/ {
			if ($2 != "arm") exit 1 }
		' control
		
	if test $? != 0; then
		rm -rf $TMPD
		msg "Downloaded wrong package?"
	fi
	
	# aufs remount /Alt-F with inotify, then back to normal
	mount -t aufs -o remount,dirs=/Alt-F,udba=inotify /
	tar -C /Alt-F -xzf data.tar.gz
	
	cd
	rm -rf $TMPD
	
	ipkg-cl -V0 update
	ipkg-cl -V0 install ipkg

	mount -t aufs -o remount,dirs=/Alt-F,udba=reval / 
	gotopage /cgi-bin/packages_ipkg.cgi
	exit 0
fi

mount -t aufs -o remount,dirs=/Alt-F,udba=inotify /
ipkg-cl -V0 update

if test -n "$Remove"; then
	res=$(ipkg-cl remove $Remove | sed -n '/Collected errors/,/^$/p' | tr '\n' ' ')

	if test -n "$res"; then
		mount -t aufs -o remount,dirs=/Alt-F,udba=reval / 
		msg "$res"
	fi

elif test -n "$Install"; then
	ipkg-cl -V0 install $Install

elif test -n "$Update"; then
	ipkg-cl -V0 install $Update

elif test -n "$UpdateAll"; then
	ipkg-cl -V0 upgrade

# done automaticaly at start.
# Wastes bandwidth, but is safer when instaling
#elif test -n "$UpdateList"; then
#	ipkg-cl -V0 update

elif test -n "$ConfigureFeed"; then
	mount -t aufs -o remount,dirs=/Alt-F,udba=reval / 
	msg "Not yet"
fi

mount -t aufs -o remount,dirs=/Alt-F,udba=reval / 

#enddebug
gotopage /cgi-bin/packages_ipkg.cgi



