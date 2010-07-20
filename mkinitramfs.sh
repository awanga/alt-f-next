#!/bin/bash

if test "$(dirname $0)" != "."; then
	echo "This script must be run in the root of the tree, exiting."
	exit 1;
fi

if test -z "$BLDDIR"; then
	cat<<-EOF
		Set the environment variable BLDDIR to the build directory, e.g
		   export BLDDIR=<path to where you which the build dir>
		Keep it out of this tree.
		Exiting.
	EOF
	exit 1
fi

if test "$#" != 1; then
	echo "Usage: mkinitramfs gz | lzma | sqfs"
	exit
fi

if test -z "$ME" -o -z "$MG"; then
	export ME=$(id -un)
	export MG=$(id -gn)
fi

if test $(whoami) != "root"; then
	sudo -E $0 $1
	exit
fi

PATH=$(pwd)/bin:$PATH
cd ${BLDDIR}/binaries/dns323

if ! test -d tmp; then
	mkdir tmp
fi

if test "$1" = "gz"; then
	mount -o loop rootfs.arm.ext2 tmp
	cd tmp
	find . | cpio --quiet -o -H newc | gzip -9 > ../rootfs.arm.cpio.gz
	cd ..
	umount tmp
	chown $ME:$MG rootfs.arm.cpio.gz

elif test "$1" = "lzma"; then
	mount -o loop rootfs.arm.ext2 tmp
	cd tmp
	find . | cpio --quiet -o -H newc | lzma e -si -so > ../rootfs.arm.cpio.lzma
	cd ..
	umount tmp
	chown $ME:$MG rootfs.arm.cpio.lzma

elif test "$1" = "sqfs"; then
	# everything squasehed
	# mount -o loop rootfs.arm.ext2 tmp
	# mksquashfs tmp/ rootfs.arm.squashfs -comp lzma -noappend

	# only /usr
	cp rootfs.arm.ext2 rootfs.arm.ext2.tmp
	mount -o loop rootfs.arm.ext2.tmp tmp
	# block sizes: 131072 262144 524288 1048576
	mksquashfs tmp/usr/ usr.squashfs -comp lzma -b 131072 \
		-always-use-fragments -keep-as-directory
	rm -rf tmp/usr/*
	mv usr.squashfs tmp
	cd tmp
	find . | cpio --quiet -o -H newc | lzma e -si -so  > ../rootfs.arm.cpio-sq.lzma
	cd ..
	umount tmp
	rm rootfs.arm.ext2.tmp

	chown $ME:$MG rootfs.arm.cpio-sq.lzma
else
	echo "Usage: mkinitramfs gz | lzma | sqfs"
fi



