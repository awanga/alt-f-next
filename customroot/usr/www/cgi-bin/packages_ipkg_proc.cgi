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

CONFF=/etc/ipkg.conf

#debug

if test "$install" = "Install"; then

	if test "$part" = "none"; then
		msg "You must select a partition"
	fi

	# create directory, aufs mount it in /Alt-F
	if ! test -h /Alt-F -a -d $(readlink -f /Alt-F); then
		part=$(httpd -d $part)
		mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)
		mkdir -p $mp/Alt-F
		ln -sf $mp/Alt-F /Alt-F
		mount -t aufs -o remount,prepend:$mp/Alt-F=rw aufs /
	fi

	IPKG=ipkg_0.99.163_arm.ipk
	FEED=$(awk '/^src/{print $3}' $CONFF)
	DESTD=$(awk '/^dest/{print $3}' $CONFF)
	
	if ! test -d "$DESTD"; then
		msg "Destination directory not found."
	fi
		
	#test if DESTDIR is a union branch
	# cat /sys/fs/aufs/si_6a606a77/br*: 
	#  /mnt/md0/Alt-F=rw
	#  /rootmnt/root=rw
	#  /rootmnt/rootsq=rr
	
	TMPD=$(mktemp -d -t)
	wget -P $TMPD $FEED/$IPKG
	if test $? != 0; then
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
		msg "Downloaded wrong package?"
	fi
	
	# FIXME aufs remount /Alt-F with inotify, then back to normal
##	mount -t aufs -o remount,dirs=/Alt-F,udba=inotify /
	tar -C /Alt-F -xzf data.tar.gz
##	mount -t aufs -o remount,dirs=/Alt-F,udba=reval / 
	
	cd
	rm -rf $TMPD
	
	ipkg-cl update
	ipkg-cl install ipkg

elif test -n "$Remove"; then
	res=$(ipkg-cl remove $Remove | sed -n '/Collected errors/,/^$/p' | tr '\n' ' ')
	if test -n "$res"; then
		msg "$res"
	fi

elif test -n "$Install"; then
	ipkg-cl -V0 install $Install

elif test -n "$Update"; then
	ipkg-cl -V0 update $Update

elif test -n "$UpdateAll"; then
	ipkg-cl -V0 upgrade
	
elif test -n "$UpdateList"; then
	ipkg-cl -V0 update

elif test -n "$ConfigureFeed"; then
	msg "Not yet"
fi

#enddebug
gotopage /cgi-bin/packages_ipkg.cgi



