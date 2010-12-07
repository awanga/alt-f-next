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
	if ! $(mountpoint -q "$mp"); then
		echo "$mp is not a mountpoint, exiting"
		exit 1
	fi

	echo "Installing Alt-F in $mp"
	if test -d $mp/Alt-F; then
		rm -f $mp/Alt-F/Alt-F $mp/Alt-F/ffp $mp/Alt-F/home
	else
		mkdir $mp/Alt-F
		echo "DON'T ADD, REMOVE OR MODIFY ANY FILE IN THIS DIRECTORY
OR ANY OF ITS SUBDIRECTORIES, OR THE SYSTEM MIGHT HANG!" > $mp/Alt-F/README.txt
	fi

	rm -f /Alt-F
	ln -s $mp/Alt-F /Alt-F
	mkdir -p /Alt-F/var
	cp -a /var/lib /var/spool /Alt-F/var
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

	mp=$(readlink -f /Alt-F)
	if test $? = 1; then
		echo "/Alt-F seems to point to nowhere, exiting. "
		exit 1
	fi

	if ! $(mountpoint -q $(dirname $mp)); then
		echo "/Alt-F is not in a mountpoint, exiting."
		exit 1
	fi
}

case $1 in
	-m)
		check
		if isaufs $mp; then
			echo "$mp is already a aufs branch."
			exit 1
		fi
		mkdir -p /Alt-F/var
		cp -a /var/lib /var/spool /Alt-F/var
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
		mount -t aufs -o remount,del:$mp /
		loadsave_settings -fa
		cp -a /Alt-F/var/* /var				
		exit $?
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
		cat /sys/fs/aufs/*/br*		
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

