#!/bin/sh

usage() {
	echo "Usage: Alt-F.sh	-m (mount the Alt-F union branch) |
		-u (umount the Alt-F union branch) |
		-n (remount with notify) |
		-r (remount with reval) |
		-l (list branches) |
		-i <mountpoint> (install in mountpoint)
		-s (status)"
	exit 1
}

install() {
	local mp
	mp="$1"
	if ! mountpoint -q "$mp"; then
		echo "$mp is not a mountpoint, exiting"
		exit 1
	fi

	echo "Installing Alt-F in $mp"
	if test -d $mp/Alt-F; then
		rm -f $mp/Alt-F/Alt-F $mp/Alt-F/ffp $mp/Alt-F/home
	else
		mkdir $mp/Alt-F
		echo "DON'T ADD, REMOVE OR MODIFY ANY FILE UNDER /ALT-F or $(realpath /Alt-F 2> /dev/null)
OR ANY OF ITS SUB-DIRECTORIES, OR THE SYSTEM MIGHT HANG!" > $mp/Alt-F/README.txt
	fi

	rm -f /Alt-F
	ln -s $mp/Alt-F /Alt-F
	
	#mkdir -p /Alt-F/var/lib /Alt-F/var/spool
	mkdir -p /Alt-F/var/lib
	for i in nfs misc; do
		cp -a /var/lib/$i /Alt-F/var/lib 
	done
	#for i in atjobs atspool cron lpd samba; do
	#	if test -d /var/spool/$i; then
	#		cp -a /var/spool/$i /Alt-F/var/spool
	#	fi
	#done
	
	loadsave_settings -ta
	mount -t aufs -o remount,prepend:$mp/Alt-F=rw /
	return $?
}

isaufs() {
	if grep -q $1 /sys/fs/aufs/*/br* 2>/dev/null; then
		return 0
	fi
	return 1
}

support() {
	if test -z "$(grep aufs /proc/filesystems)"; then
		echo "The kernel does not supports aufs, exiting."
		exit 1;
	fi

	if test -z "$(mount -t aufs)"; then
		echo "aufs does not seems to be in use, exiting."
		exit 1;
	fi
}

check() {
	support

	if ! test -e /Alt-F -a -h /Alt-F; then
		echo "/Alt-F does not exist or is not a symbolic link, exiting. "
		exit 1
	fi

	if ! mp=$(readlink -f /Alt-F); then
		echo "/Alt-F seems to point to nowhere, exiting. "
		exit 1
	fi

	if ! mountpoint -q $(dirname $mp); then
		echo "/Alt-F is not in a mountpoint, exiting."
		exit 1
	fi
}

# When Alt-F runs without packages installed, all changes to /var/spool or var/lib will
# be lost on poweroff/reboot.
# when Alt-F packages are installed on Alt-F, that directory is used as the real /var/lib
# or /var/spool, so they persist across reboots. However, as one don't know if the /Alt-F
# directory will ever appears, the system has to start anyway; when the directory appears,
# a copy operation is performed.
#
# the directory copy operations after/before mount/umounting are prone to race conditions,
# as other programs or scripts might be changing them, but can't devise any general type
# of lock to prevent that to happens.
# This occurs frequently at boot time, when hotplugging detects the Alt-F directory and
# "rcall start" is being executed. A "can't stat <file>: No such file or directory" appears.
#
# affected Alt-F directories on the base firmware:
# /var/lib/misc (rcurandom) /var/lib/nfs (rcnfs)
# /var/spool/atjobs /var/spool/atspool (rcat)
# /var/spool/cron (rccron)
# /var/spool/lpd /var/spool/samba

# lock file for initscripts (rcS) synchronization
aufslock=/tmp/.aufs-lock
dolock() {
	logger -t aufs "waiting for lock"
	while ! mkdir $aufslock >& /dev/null; do usleep 500000; done
	logger -t aufs "got lock"
}

# remove aufs lock upon termination
cleanlock() {
	logger -t aufs "remove lock"
	rmdir $aufslock
}

case $1 in
	-m)
		check
		if isaufs $mp; then
			echo "$mp is already a aufs branch."
			exit 0
		fi

		dolock
		trap cleanlock exit 

		#mkdir -p /Alt-F/var/lib /Alt-F/var/spool
		mkdir -p /Alt-F/var/lib 
		for i in nfs misc; do
			cp -a /var/lib/$i /Alt-F/var/lib 
		done
		#for i in atjobs atspool cron lpd samba; do
		#	if test -d /var/spool/$i; then
		#		cp -a /var/spool/$i /Alt-F/var/spool
		#	fi
		#done

		loadsave_settings -ta
		mount -t aufs -o remount,prepend:${mp}=rw /
		exit $?
		;;

	-u)
		check
		if ! isaufs $mp; then
			echo "$mp is not a aufs branch."
			exit 1
		fi
		if ! mount -t aufs -o remount,del:$mp / ; then
			echo "Unmounting $mp aufs branch failed, stop all services first."
			exit 1
		fi

		dolock
		trap cleanlock exit

		loadsave_settings -fa
		#mkdir -p /tmp/lib /tmp/spool
		mkdir -p /tmp/lib
		for i in nfs misc; do
			cp -a /Alt-F/var/lib/$i /tmp/lib/
		done
		#for i in atjobs atspool cron lpd samba; do
		#	if test -d /Alt-F/var/spool/$i; then
		#		cp -a /Alt-F/var/spool/$i /tmp/spool/
		#	fi
		#done
		ln -sf /tmp/lib /var/lib
		#ln -sf /tmp/spool /var/spool
		;;

	-n)
		check
		if ! isaufs $mp; then
			echo "$mp is not a aufs branch."
			exit 1
		fi
		mount -t aufs -o remount,udba=notify /
		exit $?
		;;

	-r)
		check
		if ! isaufs $mp; then
			echo "$mp is not a aufs branch."
			exit 1
		fi
		mount -t aufs -o remount,udba=reval /
		exit $?
		;;

	-l)
		mount -t aufs
		cat /sys/fs/aufs/*/br?
		;;

	-s)
		check
		if ! isaufs $mp; then
			echo "$mp is not a aufs branch."
			exit 1
		fi
		echo "OK"
		exit 0
		;;

	-i)
		support

		if isaufs Alt-F; then
			echo "/Alt-F already exists."
			exit 1

		elif test $# != 2; then
			echo "You must supply a mountpoint."
			exit 1

		else
			install $2
			exit $?
		fi
		;;

	*)
		usage
		;;
esac

