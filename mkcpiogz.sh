#!/bin/bash

if test $(whoami) != "root"; then
	sudo $0
	exit
fi

BRDIR=~jcard/Desktop/buildroot-2009.08-build-2

cd ${BRDIR}/binaries/dns323

if ! test -d tmp; then
	mkdir tmp
fi

mount -o loop rootfs.arm.ext2 tmp
cd tmp
find . | cpio --quiet -o -H newc | gzip -9 > ../rootfs.arm.cpio.gz
cd ..
umount tmp
chown jcard:users rootfs.arm.cpio.gz

